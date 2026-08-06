# -*- coding: utf-8 -*-
"""
aacp_kafka_interceptor_PLUG_BL08.py

Purpose:
- "Plug-in" interceptor for existing AACP v1 message schema, upgraded to BL-01..BL-08 enforcement.

Key properties:
- Does NOT require renaming existing message schema files.
- Adapts legacy envelope fields (agent_type -> agent_class) into BL-01 envelope model.
- Enforces:
  - Phase 1 no execute
  - Registry + Policy allow-lists (including channel/topic)
  - Chain hash verification
  - Signature verification via KeyStore
  - Reject -> DLQ always
  - Optional AuditSink append (immutable-ish)

Compatibility:
- Input message type: aacp_message_schema_v1.AACPMessage
- Input envelope type: aacp_audit_envelope_v1.AACPAuditEnvelopeV1
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from aacp_message_schema_v1 import AACPMessage
from aacp_audit_envelope_v1 import AACPAuditEnvelopeV1 as LegacyEnvelope

from aacp_bl01_audit_envelope import AACPAuditEnvelopeV1 as BL01Envelope, AgentClass
from aacp_bl02_reject_dlq import DLQPublisher
from aacp_bl03_keystore_signature import KeyStore
from aacp_bl04_registry_policy import AgentRegistryLike, PolicyResolverLike
from aacp_bl06_observability import Logger
from aacp_bl08_audit_sink import AuditSink
from aacp_bl06_08_interceptor_phase1 import intercept as _intercept


class KafkaProducerLike(Protocol):
    def produce(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        ...

    def flush(self, timeout: float = 10.0) -> None:
        ...


@dataclass(frozen=True)
class InterceptorResult:
    ok: bool
    rejected: bool
    reason_code: Optional[str] = None
    reason: Optional[str] = None


def _adapt_envelope(legacy: LegacyEnvelope) -> BL01Envelope:
    d = legacy.dict()

    # Map legacy agent_type -> BL-01 agent_class (same value set in Phase 1)
    agent_type_val = d.pop("agent_type")
    d["agent_class"] = AgentClass(agent_type_val)

    # BL-01 expects channel/topic/flow already present (they are)
    return BL01Envelope(**d)


class KafkaAACPInterceptor_PLUG_BL08:
    def __init__(
        self,
        *,
        producer: KafkaProducerLike,
        dlq_publisher: DLQPublisher,
        agent_registry: AgentRegistryLike,
        policy_resolver: PolicyResolverLike,
        keystore: KeyStore,
        audit_sink: Optional[AuditSink] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._producer = producer
        self._dlq = dlq_publisher
        self._registry = agent_registry
        self._policies = policy_resolver
        self._keystore = keystore
        self._audit_sink = audit_sink
        self._logger = logger or Logger("aacp.interceptor.plug.bl08", enabled=True)

    def publish(self, *, topic: str, msg: AACPMessage, key: Optional[str] = None) -> InterceptorResult:
        # This interceptor validates + (optionally) writes audit record, then publishes the message bytes.
        # Payload is the dict under msg.payload.data in v1 schema.
        payload_dict: Dict[str, Any] = msg.payload.data

        # Adapt envelope to BL-01
        env = _adapt_envelope(msg.audit)

        result = _intercept(
            channel_id=env.channel_id,
            topic=topic,
            message=msg,
            envelope=env,
            payload=payload_dict,
            agent_registry=self._registry,
            policy_resolver=self._policies,
            keystore=self._keystore,
            dlq_publisher=self._dlq,
            audit_sink=self._audit_sink,
            logger=self._logger,
            context=None,
        )

        if not result.ok:
            return InterceptorResult(ok=False, rejected=True, reason_code=result.reason_code, reason=result.reason)

        # Publish: keep legacy schema payload layout, but attach the BL-01 compatible envelope as msg.audit snapshot.
        # This avoids breaking consumers that parse AACPMessage v1.
        # We publish msg.json() exactly as the caller built it; auditing is already done.
        value = msg.json(by_alias=False, ensure_ascii=False).encode("utf-8")
        headers = {"type": "AACP_MESSAGE", "schema": "1.0"}
        self._producer.produce(topic=topic, key=key or env.trace_id, value=value, headers=headers)
        return InterceptorResult(ok=True, rejected=False)
