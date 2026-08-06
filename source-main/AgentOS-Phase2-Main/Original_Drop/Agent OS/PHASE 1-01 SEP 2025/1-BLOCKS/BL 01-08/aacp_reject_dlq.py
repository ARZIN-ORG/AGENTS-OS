# aacp_reject_dlq.py
# -*- coding: utf-8 -*-
"""
BL-02 — Reject & DLQ Handler (Phase 1)

Design intent:
- No silent drops
- No auto-retry
- Reject is an event with immutable intent
- DLQ topic is deterministic and auditable

This module is deliberately strict. If it cannot enforce, it rejects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional, Protocol


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


class RejectReasonCode(str, Enum):
    ENVELOPE_MISSING = "ENVELOPE_MISSING"
    ENVELOPE_INVALID = "ENVELOPE_INVALID"
    EXECUTE_FORBIDDEN = "EXECUTE_FORBIDDEN"
    CHAIN_HASH_MISMATCH = "CHAIN_HASH_MISMATCH"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    SIG_VERIFY_UNCONFIGURED = "SIG_VERIFY_UNCONFIGURED"
    AGENT_NOT_REGISTERED = "AGENT_NOT_REGISTERED"
    POLICY_MISMATCH = "POLICY_MISMATCH"
    INTERNAL_ERROR = "INTERNAL_ERROR"


@dataclass(frozen=True)
class RejectEvent:
    version: str
    rejected_at: str
    reason_code: str
    reason: str
    original_topic: str
    dlq_topic: str
    trace_id: Optional[str]
    message_id: Optional[str]
    agent_id: Optional[str]
    policy_id: Optional[str]
    policy_version: Optional[str]
    envelope_snapshot: Optional[Dict[str, Any]]
    message_snapshot: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "rejected_at": self.rejected_at,
            "reason_code": self.reason_code,
            "reason": self.reason,
            "original_topic": self.original_topic,
            "dlq_topic": self.dlq_topic,
            "trace_id": self.trace_id,
            "message_id": self.message_id,
            "agent_id": self.agent_id,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "envelope_snapshot": self.envelope_snapshot,
            "message_snapshot": self.message_snapshot,
        }


class DLQPublisher(Protocol):
    """Abstraction to keep Kafka/NATS out of BL-02."""

    def publish(self, topic: str, key: Optional[str], value: bytes, headers: Optional[Dict[str, str]] = None) -> None:
        ...


def default_dlq_topic(original_topic: str) -> str:
    return f"{original_topic}.DLQ"


def build_reject_event(
    *,
    original_topic: str,
    reason_code: RejectReasonCode,
    reason: str,
    envelope_snapshot: Optional[Dict[str, Any]] = None,
    message_snapshot: Optional[Dict[str, Any]] = None,
) -> RejectEvent:
    dlq_topic = default_dlq_topic(original_topic)

    trace_id = None
    message_id = None
    agent_id = None
    policy_id = None
    policy_version = None

    if envelope_snapshot:
        trace_id = envelope_snapshot.get("trace_id")
        message_id = envelope_snapshot.get("message_id")
        agent_id = envelope_snapshot.get("agent_id")
        policy_id = envelope_snapshot.get("policy_id")
        policy_version = envelope_snapshot.get("policy_version")

    return RejectEvent(
        version="1.0",
        rejected_at=utc_now_z(),
        reason_code=reason_code.value,
        reason=reason,
        original_topic=original_topic,
        dlq_topic=dlq_topic,
        trace_id=trace_id,
        message_id=message_id,
        agent_id=agent_id,
        policy_id=policy_id,
        policy_version=policy_version,
        envelope_snapshot=envelope_snapshot,
        message_snapshot=message_snapshot,
    )


def publish_reject(
    *,
    publisher: DLQPublisher,
    reject_event: RejectEvent,
) -> None:
    payload = canonical_json_bytes(reject_event.to_dict())
    key = reject_event.trace_id or reject_event.message_id or None
    headers = {"type": "AACP_REJECT_EVENT", "version": reject_event.version}
    publisher.publish(topic=reject_event.dlq_topic, key=key, value=payload, headers=headers)
