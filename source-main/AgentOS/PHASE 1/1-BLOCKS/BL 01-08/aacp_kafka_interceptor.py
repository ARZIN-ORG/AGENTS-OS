# aacp_kafka_interceptor.py
# -*- coding: utf-8 -*-
"""
Kafka Interceptor for AACP (Phase 1)

Purpose:
- Enforce BL-01 (Audit Envelope is mandatory and valid)
- Enforce BL-02 (Reject -> DLQ event, deterministic)
- Fail-fast before publish (no silent bypass)

This interceptor is intentionally simple: validate -> publish OR reject -> DLQ.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Protocol, Tuple

from pydantic import ValidationError

from aacp_audit_envelope_v1 import AACPAuditEnvelopeV1, DecisionClass, compute_chain_hash
from aacp_message_schema_v1 import AACPMessage
from aacp_reject_dlq import (
    DLQPublisher,
    RejectReasonCode,
    build_reject_event,
    publish_reject,
)


class KafkaProducerLike(Protocol):
    def produce(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        ...

    def flush(self, timeout: float = 10.0) -> None:
        ...


class AgentRegistryLike(Protocol):
    def is_registered(self, agent_id: str) -> bool:
        ...


class PolicyResolverLike(Protocol):
    def is_policy_active(self, policy_id: str, policy_version: str) -> bool:
        ...


SignatureVerifier = Callable[[AACPAuditEnvelopeV1, Dict[str, Any]], bool]
# signature verifier receives (envelope, payload_dict) and must return True/False.


@dataclass(frozen=True)
class InterceptorResult:
    ok: bool
    rejected: bool
    reason_code: Optional[str] = None
    reason: Optional[str] = None


def _message_to_snapshot(msg: Any) -> Dict[str, Any]:
    if hasattr(msg, "dict"):
        return msg.dict()
    if isinstance(msg, dict):
        return msg
    raise TypeError("message must be AACPMessage or dict")


def _envelope_without_chain(env: AACPAuditEnvelopeV1) -> Dict[str, Any]:
    d = env.dict()
    d.pop("chain_hash", None)
    return d


def validate_message_phase1(
    *,
    msg: AACPMessage,
    agent_registry: Optional[AgentRegistryLike],
    policy_resolver: Optional[PolicyResolverLike],
    signature_verifier: Optional[SignatureVerifier],
) -> Tuple[bool, Optional[RejectReasonCode], str]:
    # 1) Pydantic validation already happened by constructing AACPMessage & AACPAuditEnvelopeV1
    env = msg.audit

    # 2) Phase 1: execute forbidden (also validated in model, but keep explicit)
    if env.decision_class == DecisionClass.execute:
        return False, RejectReasonCode.EXECUTE_FORBIDDEN, "Phase 1 forbids decision_class=execute"

    # 3) Registry gate (strict)
    if agent_registry is not None:
        if not agent_registry.is_registered(env.agent_id):
            return False, RejectReasonCode.AGENT_NOT_REGISTERED, "agent_id is not registered"
    else:
        # strict: if registry is not wired, reject rather than bypass
        return False, RejectReasonCode.INTERNAL_ERROR, "agent_registry is not configured"

    # 4) Policy gate (strict)
    if policy_resolver is not None:
        if not policy_resolver.is_policy_active(env.policy_id, env.policy_version):
            return False, RejectReasonCode.POLICY_MISMATCH, "policy_id/policy_version not active"
    else:
        return False, RejectReasonCode.INTERNAL_ERROR, "policy_resolver is not configured"

    # 5) Chain hash gate
    payload_dict = msg.payload.data if hasattr(msg.payload, "data") else msg.payload.dict()
    expected = compute_chain_hash(
        envelope_without_chain=_envelope_without_chain(env),
        payload=payload_dict,
        prev_chain_hash=env.prev_chain_hash,
    )
    if env.chain_hash != expected:
        return False, RejectReasonCode.CHAIN_HASH_MISMATCH, "chain_hash mismatch"

    # 6) Signature gate (strict): must be configured
    if signature_verifier is None:
        return False, RejectReasonCode.SIG_VERIFY_UNCONFIGURED, "signature_verifier not configured"
    ok = signature_verifier(env, payload_dict)
    if not ok:
        return False, RejectReasonCode.SIGNATURE_INVALID, "signature verification failed"

    return True, None, "ok"


class KafkaAACPInterceptor:
    """Validate AACP messages before publishing to Kafka; reject to DLQ if invalid."""

    def __init__(
        self,
        *,
        producer: KafkaProducerLike,
        dlq_publisher: DLQPublisher,
        agent_registry: AgentRegistryLike,
        policy_resolver: PolicyResolverLike,
        signature_verifier: SignatureVerifier,
    ) -> None:
        self._producer = producer
        self._dlq = dlq_publisher
        self._agent_registry = agent_registry
        self._policy_resolver = policy_resolver
        self._signature_verifier = signature_verifier

    def publish(self, *, topic: str, msg: AACPMessage, key: Optional[str] = None) -> InterceptorResult:
        try:
            ok, code, reason = validate_message_phase1(
                msg=msg,
                agent_registry=self._agent_registry,
                policy_resolver=self._policy_resolver,
                signature_verifier=self._signature_verifier,
            )
            if not ok:
                self._reject(topic=topic, msg=msg, reason_code=code or RejectReasonCode.INTERNAL_ERROR, reason=reason)
                return InterceptorResult(ok=False, rejected=True, reason_code=(code or RejectReasonCode.INTERNAL_ERROR).value, reason=reason)

            # publish canonical json of full message
            snapshot = msg.dict()
            value = __import__("json").dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            k = key or msg.audit.trace_id or msg.audit.message_id
            self._producer.produce(topic=topic, key=k, value=value, headers={"type": "AACP_MESSAGE", "version": msg.audit.envelope_version.value})
            return InterceptorResult(ok=True, rejected=False)

        except ValidationError as ve:
            self._reject(topic=topic, msg=msg, reason_code=RejectReasonCode.ENVELOPE_INVALID, reason=str(ve))
            return InterceptorResult(ok=False, rejected=True, reason_code=RejectReasonCode.ENVELOPE_INVALID.value, reason=str(ve))

        except Exception as ex:
            self._reject(topic=topic, msg=msg, reason_code=RejectReasonCode.INTERNAL_ERROR, reason=str(ex))
            return InterceptorResult(ok=False, rejected=True, reason_code=RejectReasonCode.INTERNAL_ERROR.value, reason=str(ex))

    def _reject(self, *, topic: str, msg: AACPMessage, reason_code: RejectReasonCode, reason: str) -> None:
        env_snapshot = msg.audit.dict() if hasattr(msg, "audit") and msg.audit is not None else None
        msg_snapshot = msg.dict() if hasattr(msg, "dict") else None
        evt = build_reject_event(
            original_topic=topic,
            reason_code=reason_code,
            reason=reason,
            envelope_snapshot=env_snapshot,
            message_snapshot=msg_snapshot,
        )
        publish_reject(publisher=self._dlq, reject_event=evt)
