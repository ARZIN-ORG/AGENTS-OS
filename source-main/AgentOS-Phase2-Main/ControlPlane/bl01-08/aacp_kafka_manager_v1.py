# aacp_kafka_manager_v1.py
# -*- coding: utf-8 -*-
"""
AACP Kafka Manager (Revised)
- Interceptor-first publish path
- Enforces BL-01 (Audit Envelope)
- Enforces BL-02 (Reject & DLQ)
"""

from __future__ import annotations

from typing import Dict, Optional

from aacp_kafka_interceptor import KafkaAACPInterceptor
from aacp_message_schema_v1 import AACPMessage
from aacp_reject_dlq import DLQPublisher


class KafkaProducerWrapper:
    """Thin wrapper around actual Kafka producer."""

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
    """Single entry point for producing AACP messages."""

    def __init__(
        self,
        *,
        producer,
        agent_registry,
        policy_resolver,
        signature_verifier,
    ) -> None:
        wrapped_producer = KafkaProducerWrapper(producer)
        dlq_publisher = KafkaDLQPublisher(producer)

        self._interceptor = KafkaAACPInterceptor(
            producer=wrapped_producer,
            dlq_publisher=dlq_publisher,
            agent_registry=agent_registry,
            policy_resolver=policy_resolver,
            signature_verifier=signature_verifier,
        )

    def publish(self, *, topic: str, msg: AACPMessage, key: Optional[str] = None) -> None:
        result = self._interceptor.publish(topic=topic, msg=msg, key=key)
        if not result.ok:
            # Fail-fast: caller must handle rejection explicitly
            raise RuntimeError(f"AACP publish rejected: {result.reason_code} - {result.reason}")
