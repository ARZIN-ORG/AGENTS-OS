from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PolicyScope:
    """Policy scope identifier (must be bound, never implicit)."""
    value: str

@dataclass(frozen=True)
class ChannelBinding:
    """Channel binding for publish/consume. No wildcard by default."""
    topic: str
