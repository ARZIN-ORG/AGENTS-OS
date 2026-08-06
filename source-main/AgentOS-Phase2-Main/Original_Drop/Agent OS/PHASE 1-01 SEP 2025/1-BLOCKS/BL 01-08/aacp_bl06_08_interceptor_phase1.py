
# -*- coding: utf-8 -*-
"""
Phase 1 Interceptor (BL-01..BL-04..BL-07..BL-08)

This is a transport-agnostic validator+auditor.
- Validate envelope + registry + policy + chain hash + signature
- On failure: emit reject event via BL-02 publisher
- On success: append minimal audit record via BL-08 sink (optional but recommended)

This file exists to keep the main Kafka integration thin.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Tuple

from pydantic import ValidationError

from aacp_bl01_audit_envelope import AACPAuditEnvelopeV1, DecisionClass, compute_chain_hash, envelope_without_chain
from aacp_bl02_reject_dlq import DLQPublisher, RejectReasonCode, build_reject_event, publish_reject
from aacp_bl03_keystore_signature import KeyStore, verify_signature
from aacp_bl04_registry_policy import AgentRegistryLike, PolicyResolverLike
from aacp_bl06_observability import Logger, audit_fields
from aacp_bl08_audit_sink import AuditSink

class MessageSchema(Protocol):
    def dict(self) -> Dict[str, Any]:
        ...

@dataclass(frozen=True)
class InterceptorResult:
    ok: bool
    rejected: bool
    reason_code: Optional[str] = None
    reason: Optional[str] = None

def validate_phase1(
    *,
    env: AACPAuditEnvelopeV1,
    payload: Dict[str, Any],
    agent_registry: AgentRegistryLike,
    policy_resolver: PolicyResolverLike,
    keystore: KeyStore,
) -> Tuple[bool, Optional[RejectReasonCode], str]:
    if env.decision_class == DecisionClass.execute:
        return False, RejectReasonCode.EXECUTE_FORBIDDEN, "Phase 1 forbids decision_class=execute"

    if not agent_registry.is_registered(env.agent_id):
        return False, RejectReasonCode.AGENT_NOT_REGISTERED, "agent_id is not registered"

    # Agent allow-lists
    if env.channel_id not in agent_registry.allowed_channels(env.agent_id):
        return False, RejectReasonCode.CHANNEL_NOT_ALLOWED, "agent not allowed for channel_id"
    if env.topic not in agent_registry.allowed_topics(env.agent_id):
        return False, RejectReasonCode.TOPIC_NOT_ALLOWED, "agent not allowed for topic"

    # Policy allow-lists
    if not policy_resolver.is_policy_active(env.policy_id, env.policy_version):
        return False, RejectReasonCode.POLICY_MISMATCH, "policy_id/policy_version not active"
    if env.decision_class.value not in policy_resolver.allowed_decision_classes(env.policy_id, env.policy_version):
        return False, RejectReasonCode.POLICY_MISMATCH, "decision_class not allowed by policy"
    if env.channel_id not in policy_resolver.allowed_channels(env.policy_id, env.policy_version):
        return False, RejectReasonCode.POLICY_MISMATCH, "channel_id not allowed by policy"
    if env.topic not in policy_resolver.allowed_topics(env.policy_id, env.policy_version):
        return False, RejectReasonCode.POLICY_MISMATCH, "topic not allowed by policy"

    expected = compute_chain_hash(envelope_wo_chain=envelope_without_chain(env), payload=payload, prev_chain_hash=env.prev_chain_hash)
    if env.chain_hash != expected:
        return False, RejectReasonCode.CHAIN_HASH_MISMATCH, "chain_hash mismatch"

    if not verify_signature(envelope=env, payload=payload, keystore=keystore):
        return False, RejectReasonCode.SIGNATURE_INVALID, "signature verification failed"

    return True, None, "ok"

def intercept(
    *,
    channel_id: str,
    topic: str,
    message: MessageSchema,
    envelope: AACPAuditEnvelopeV1,
    payload: Dict[str, Any],
    agent_registry: AgentRegistryLike,
    policy_resolver: PolicyResolverLike,
    keystore: KeyStore,
    dlq_publisher: DLQPublisher,
    audit_sink: Optional[AuditSink],
    logger: Logger,
    context: Optional[Dict[str, Any]] = None,
) -> InterceptorResult:
    try:
        ok, code, reason = validate_phase1(
            env=envelope,
            payload=payload,
            agent_registry=agent_registry,
            policy_resolver=policy_resolver,
            keystore=keystore,
        )
        if not ok:
            evt = build_reject_event(
                channel_id=channel_id,
                original_topic=topic,
                reason_code=code or RejectReasonCode.INTERNAL_ERROR,
                reason=reason,
                envelope_snapshot=envelope.dict(),
                message_snapshot=message.dict(),
                context=context,
            )
            publish_reject(publisher=dlq_publisher, reject_event=evt)
            logger.warn("aacp_reject", **audit_fields(trace_id=envelope.trace_id, message_id=envelope.message_id, channel_id=channel_id, topic=topic), reason_code=evt.reason_code)
            return InterceptorResult(ok=False, rejected=True, reason_code=evt.reason_code, reason=reason)

        if audit_sink is not None:
            audit_sink.append({
                "type": "AACP_AUDIT",
                "version": envelope.envelope_version.value,
                "trace_id": envelope.trace_id,
                "message_id": envelope.message_id,
                "agent_id": envelope.agent_id,
                "agent_class": envelope.agent_class.value,
                "agent_version": envelope.agent_version,
                "channel_id": envelope.channel_id,
                "topic": envelope.topic,
                "flow_id": envelope.flow_id,
                "policy_id": envelope.policy_id,
                "policy_version": envelope.policy_version,
                "decision_class": envelope.decision_class.value,
                "event_time": envelope.event_time,
                "ingest_time": envelope.ingest_time,
                "chain_hash": envelope.chain_hash,
                "prev_chain_hash": envelope.prev_chain_hash,
            })

        logger.info("aacp_accept", **audit_fields(trace_id=envelope.trace_id, message_id=envelope.message_id, channel_id=channel_id, topic=topic))
        return InterceptorResult(ok=True, rejected=False)

    except ValidationError as ve:
        evt = build_reject_event(
            channel_id=channel_id,
            original_topic=topic,
            reason_code=RejectReasonCode.ENVELOPE_INVALID,
            reason=str(ve),
            envelope_snapshot=envelope.dict() if envelope else None,
            message_snapshot=message.dict(),
            context=context,
        )
        publish_reject(publisher=dlq_publisher, reject_event=evt)
        logger.error("aacp_reject_validation_error", error=str(ve))
        return InterceptorResult(ok=False, rejected=True, reason_code=evt.reason_code, reason=str(ve))

    except Exception as ex:
        evt = build_reject_event(
            channel_id=channel_id,
            original_topic=topic,
            reason_code=RejectReasonCode.INTERNAL_ERROR,
            reason=str(ex),
            envelope_snapshot=envelope.dict() if envelope else None,
            message_snapshot=message.dict(),
            context=context,
        )
        publish_reject(publisher=dlq_publisher, reject_event=evt)
        logger.error("aacp_reject_internal_error", error=str(ex))
        return InterceptorResult(ok=False, rejected=True, reason_code=evt.reason_code, reason=str(ex))
