# aacp_kafka_manager_v2.py
# -*- coding: utf-8 -*-
"""
AACP Kafka Manager (Revised - Wired Signature Verification)

What this changes vs v1:
- Signature verification is wired end-to-end via KeyStore.
- No placeholder verifier. No bypass. If keystore missing => reject.

Enforces:
- BL-01: Audit Envelope mandatory
- BL-02: Reject -> DLQ
- Signature verification mandatory (Phase 1)
"""

from __future__ import annotations

from typing import Dict, Optional

from aacp_kafka_interceptor import KafkaAACPInterceptor
from aacp_message_schema_v1 import AACPMessage
from aacp_reject_dlq import DLQPublisher
from aacp_signature_verifier import verify_signature, KeyStore


class KafkaProducerWrapper:
    """Thin wrapper around actual Kafka producer (confluent-kafka or compatible)."""

    def __init__(self, producer):
        self._producer = producer

    def produce(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        self._producer.produce(topic=topic, key=key, value=value, headers=headers)

    def flush(self, timeout: float = 10.0) -> None:
        self._producer.flush(timeout)


class KafkaDLQPublisher(DLQPublisher):
    """DLQ publisher using the same Kafka cluster."""

    def __init__(self, producer):
        self._producer = producer

    def publish(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        self._producer.produce(topic=topic, key=key, value=value, headers=headers)


class AACKafkaManager:
    """
    Single entry point for producing AACP messages in Private Cloud.

    Strict behavior:
    - Any validation failure => DLQ + exception
    - No silent drop
    - No auto-retry
    """

    def __init__(
        self,
        *,
        producer,
        agent_registry,
        policy_resolver,
        keystore: KeyStore,
    ) -> None:
        if keystore is None:
            raise ValueError("keystore is required (no bypass)")

        wrapped_producer = KafkaProducerWrapper(producer)
        dlq_publisher = KafkaDLQPublisher(producer)

        def _signature_verifier(env, payload) -> bool:
            return verify_signature(envelope=env, payload=payload, keystore=keystore)

        self._interceptor = KafkaAACPInterceptor(
            producer=wrapped_producer,
            dlq_publisher=dlq_publisher,
            agent_registry=agent_registry,
            policy_resolver=policy_resolver,
            signature_verifier=_signature_verifier,
        )

    def publish(self, *, topic: str, msg: AACPMessage, key: Optional[str] = None) -> None:
        result = self._interceptor.publish(topic=topic, msg=msg, key=key)
        if not result.ok:
            raise RuntimeError(f"AACP publish rejected: {result.reason_code} - {result.reason}")
