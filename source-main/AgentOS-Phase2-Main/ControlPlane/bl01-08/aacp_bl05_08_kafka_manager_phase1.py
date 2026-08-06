# -*- coding: utf-8 -*-
"""
Kafka Manager — Phase 1 (BL-01..BL-08)

Design goals:
- Single allowed publish entry point
- Multi-channel routing (ChannelManager)
- Strict enforcement:
  - Envelope required
  - Phase 1 no execute
  - Registry + Policy allow-lists
  - Chain hash verification
  - Signature verification via KeyStore
  - Reject -> DLQ always
  - Optional AuditSink append

This file intentionally avoids framework glue.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from aacp_bl01_audit_envelope import AACPAuditEnvelopeV1
from aacp_bl02_reject_dlq import DLQPublisher
from aacp_bl03_keystore_signature import KeyStore
from aacp_bl04_registry_policy import AgentRegistryLike, PolicyResolverLike
from aacp_bl05_channel_manager import ChannelManager, ProducerLike
from aacp_bl06_observability import Logger
from aacp_bl07_message_codec import encode_message
from aacp_bl08_audit_sink import AuditSink
from aacp_bl06_08_interceptor_phase1 import intercept


class MessageLike(Protocol):
    def dict(self) -> Dict[str, Any]:
        ...


@dataclass
class KafkaDLQPublisher(DLQPublisher):
    producer: ProducerLike
    dlq_topic: str

    def publish(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        # topic is provided by BL-02, ignore dlq_topic field; keep for compatibility.
        self.producer.produce(topic=topic, key=key, value=value, headers=headers)


class AACPKafkaManagerPhase1:
    def __init__(
        self,
        *,
        channel_manager: ChannelManager,
        agent_registry: AgentRegistryLike,
        policy_resolver: PolicyResolverLike,
        keystore: KeyStore,
        audit_sink: Optional[AuditSink],
        logger: Optional[Logger] = None,
    ) -> None:
        self._channels = channel_manager
        self._registry = agent_registry
        self._policies = policy_resolver
        self._keystore = keystore
        self._audit_sink = audit_sink
        self._logger = logger or Logger("aacp.kafka.phase1", enabled=True)

    def publish(
        self,
        *,
        channel_id: str,
        topic: str,
        message: MessageLike,
        envelope: AACPAuditEnvelopeV1,
        payload: Dict[str, Any],
        key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        # Channel routing
        producer = self._channels.producer_for(channel_id)
        dlq_pub = KafkaDLQPublisher(producer=producer, dlq_topic="")  # BL-02 picks the topic

        # Intercept (validate + reject + optional audit)
        result = intercept(
            channel_id=channel_id,
            topic=topic,
            message=message,
            envelope=envelope,
            payload=payload,
            agent_registry=self._registry,
            policy_resolver=self._policies,
            keystore=self._keystore,
            dlq_publisher=dlq_pub,
            audit_sink=self._audit_sink,
            logger=self._logger,
            context=None,
        )
        if not result.ok:
            raise RuntimeError(f"AACP publish rejected: {result.reason_code} - {result.reason}")

        # Encode and publish the real message
        full = message.dict()
        full["audit"] = envelope.dict()
        full["payload"] = payload
        encoded = encode_message(full)

        producer.produce(
            topic=self._channels.topic_for(channel_id, topic),
            key=key or envelope.trace_id,
            value=encoded.value,
            headers={**(headers or {}), "type": "AACP_MESSAGE", "schema": "1.0", "payload_hash": encoded.payload_hash},
        )
