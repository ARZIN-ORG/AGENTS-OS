# -*- coding: utf-8 -*-
"""
aacp_kafka_manager_PLUG_BL08.py

Purpose:
- Plug-in Kafka manager wiring existing codebase to BL-01..BL-08 enforcement.
- Multi-channel routing via ChannelManager (BL-05).
- Uses KafkaAACPInterceptor_PLUG_BL08 internally.

This file is designed for Private Cloud:
- No external discovery.
- All allow-lists come from config files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from aacp_message_schema_v1 import AACPMessage

from aacp_bl05_channel_manager import ChannelManager, ProducerLike
from aacp_bl03_keystore_signature import KeyStore, FileKeyStore
from aacp_bl04_registry_policy import (
    AgentRegistryLike,
    PolicyResolverLike,
    load_registry_from_json,
    load_policies_from_json,
)
from aacp_bl06_observability import Logger
from aacp_bl08_audit_sink import AuditSink, AuditSinkGuard, FileAuditSink, KafkaAuditSink

from aacp_kafka_interceptor_PLUG_BL08 import KafkaAACPInterceptor_PLUG_BL08


class KafkaProducerFactory(Protocol):
    def producer_for_alias(self, broker_alias: str) -> ProducerLike:
        ...


@dataclass(frozen=True)
class PlugConfig:
    """
    Paths are optional; you can also inject objects directly.
    """
    channels_json: str
    registry_json: str
    policies_json: str
    keystore_json: str

    # Audit sink config
    audit_mode: str = "kafka"  # "kafka" or "file" or "off"
    audit_kafka_topic: str = "AACP.AUDIT"
    audit_file_path: str = "./aacp_audit.log"
    audit_fail_fast: bool = True


class AACPKafkaManager_PLUG_BL08:
    def __init__(
        self,
        *,
        channel_manager: ChannelManager,
        agent_registry: AgentRegistryLike,
        policy_resolver: PolicyResolverLike,
        keystore: KeyStore,
        logger: Optional[Logger] = None,
        audit_sink: Optional[AuditSink] = None,
    ) -> None:
        self._channels = channel_manager
        self._registry = agent_registry
        self._policies = policy_resolver
        self._keystore = keystore
        self._logger = logger or Logger("aacp.kafka.plug.bl08", enabled=True)
        self._audit_sink = audit_sink  # optional

    @classmethod
    def from_files(
        cls,
        *,
        cfg: PlugConfig,
        producers_by_alias: Dict[str, ProducerLike],
        logger: Optional[Logger] = None,
    ) -> "AACPKafkaManager_PLUG_BL08":
        # Control plane (allow-lists)
        registry = load_registry_from_json(cfg.registry_json)
        policies = load_policies_from_json(cfg.policies_json)
        keystore = FileKeyStore.from_json_file(cfg.keystore_json)

        # Multi-channel
        channel_manager = ChannelManager.from_json_file(cfg.channels_json, producers=producers_by_alias)

        # Audit sink
        audit_sink: Optional[AuditSink] = None
        if cfg.audit_mode == "off":
            audit_sink = None
        elif cfg.audit_mode == "file":
            audit_sink = AuditSinkGuard(
                sink=FileAuditSink(path=cfg.audit_file_path, fsync=False),
                logger=logger or Logger("aacp.audit.sink", enabled=True),
                fail_fast=cfg.audit_fail_fast,
            )
        elif cfg.audit_mode == "kafka":
            # Use the first producer as audit producer by default.
            # In real deployments, you may wire a dedicated broker alias.
            if not producers_by_alias:
                raise ValueError("no producers configured for kafka audit sink")
            any_producer = next(iter(producers_by_alias.values()))
            audit_sink = AuditSinkGuard(
                sink=KafkaAuditSink(producer=any_producer, topic=cfg.audit_kafka_topic),
                logger=logger or Logger("aacp.audit.sink", enabled=True),
                fail_fast=cfg.audit_fail_fast,
            )
        else:
            raise ValueError("invalid audit_mode; expected kafka|file|off")

        return cls(
            channel_manager=channel_manager,
            agent_registry=registry,
            policy_resolver=policies,
            keystore=keystore,
            logger=logger,
            audit_sink=audit_sink,
        )

    def publish(self, *, channel_id: str, topic: str, msg: AACPMessage, key: Optional[str] = None) -> None:
        # Route by channel
        producer = self._channels.producer_for(channel_id)

        # DLQ publisher uses same producer; BL-02 decides DLQ topic name.
        dlq_publisher = _DLQPublisher(producer)

        interceptor = KafkaAACPInterceptor_PLUG_BL08(
            producer=producer,
            dlq_publisher=dlq_publisher,
            agent_registry=self._registry,
            policy_resolver=self._policies,
            keystore=self._keystore,
            audit_sink=self._audit_sink,
            logger=self._logger,
        )

        result = interceptor.publish(topic=self._channels.topic_for(channel_id, topic), msg=msg, key=key)
        if not result.ok:
            raise RuntimeError(f"AACP publish rejected: {result.reason_code} - {result.reason}")


class _DLQPublisher:
    def __init__(self, producer: ProducerLike) -> None:
        self._producer = producer

    def publish(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        self._producer.produce(topic=topic, key=key, value=value, headers=headers)
