
# -*- coding: utf-8 -*-
"""
BL-05 — Multi-Channel Manager (Phase 1)

Locked behavior:
- Multi-channel is mandatory (explicit channel_id in every message).
- Channels are allow-listed in config.
- If channel not configured => reject/fail-fast.
- Private Cloud friendly: local config, no external discovery.

This module provides:
- Channel routing (which Kafka cluster/producer to use)
- DLQ naming convention helper
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Tuple

class ProducerLike(Protocol):
    def produce(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        ...
    def flush(self, timeout: float = 10.0) -> None:
        ...

@dataclass(frozen=True)
class ChannelConfig:
    channel_id: str
    broker_alias: str
    topic_prefix: str = ""  # optional, e.g., "aacp."
    dlq_prefix: str = ""    # optional
    enabled: bool = True

@dataclass
class ChannelManager:
    channels: Dict[str, ChannelConfig]
    producers: Dict[str, ProducerLike]  # broker_alias -> producer

    @classmethod
    def from_json_file(cls, path: str, *, producers: Dict[str, ProducerLike]) -> "ChannelManager":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "channels" not in data or not isinstance(data["channels"], list):
            raise ValueError("invalid channels json; expected {'channels':[...]}")

        channels: Dict[str, ChannelConfig] = {}
        for item in data["channels"]:
            if not isinstance(item, dict):
                raise ValueError("invalid channel entry")
            cfg = ChannelConfig(
                channel_id=str(item["channel_id"]),
                broker_alias=str(item["broker_alias"]),
                topic_prefix=str(item.get("topic_prefix", "")),
                dlq_prefix=str(item.get("dlq_prefix", "")),
                enabled=bool(item.get("enabled", True)),
            )
            channels[cfg.channel_id] = cfg

        return cls(channels=channels, producers=producers)

    def require_channel(self, channel_id: str) -> ChannelConfig:
        cfg = self.channels.get(channel_id)
        if not cfg or not cfg.enabled:
            raise ValueError(f"channel not configured/enabled: {channel_id}")
        if cfg.broker_alias not in self.producers:
            raise ValueError(f"producer not registered for broker_alias: {cfg.broker_alias}")
        return cfg

    def producer_for(self, channel_id: str) -> ProducerLike:
        cfg = self.require_channel(channel_id)
        return self.producers[cfg.broker_alias]

    def topic_for(self, channel_id: str, topic: str) -> str:
        cfg = self.require_channel(channel_id)
        return f"{cfg.topic_prefix}{topic}"

    def dlq_topic_for(self, channel_id: str, topic: str) -> str:
        cfg = self.require_channel(channel_id)
        # Deterministic, channel-scoped
        return f"{cfg.dlq_prefix}{channel_id}.{topic}.DLQ"
