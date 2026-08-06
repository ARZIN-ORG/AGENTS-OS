# -*- coding: utf-8 -*-
"""
ARZIN / AACP — Reject & DLQ Handler v2 (Phase-1)
File: aacp_bl02_reject_dlq_v2.py

- Builds strict DLQ events.
- Publishes via an abstract DlqPublisher.
- If publish fails: caller must fail-closed (do not pass traffic).
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional, Protocol

from aacp_dlq_event_schema_v2 import DlqEvent, DlqEnvelope, DlqDecision

class DlqPublisher(Protocol):
    def publish(self, topic: str, key: str, value_bytes: bytes, headers: Optional[Dict[str, str]] = None) -> None: ...

def build_dlq_event(
    *,
    agent_id: str,
    agent_class: str,
    channel_id: str,
    topic: str,
    envelope: Dict[str, Any],
    reason_code: str,
    gate: str,
    policy_id: str | None = None,
    policy_version: int | None = None,
) -> DlqEvent:
    env = DlqEnvelope(
        trace_id=str(envelope.get("trace_id", "")),
        message_id=envelope.get("message_id"),
        channel_id=channel_id,
        topic=topic,
        payload_bytes=int(envelope.get("payload_bytes", 0)),
        ttl_seconds=int(envelope.get("ttl_seconds", 0)),
        signature_valid=bool(envelope.get("signature_valid", False)),
        chain_hash=envelope.get("chain_hash"),
        envelope_hash=envelope.get("envelope_hash"),
    )
    dec = DlqDecision(
        decision="DENY",
        reason_code=reason_code,
        policy_id=policy_id,
        policy_version=policy_version,
        gate=gate,
    )
    return DlqEvent(agent_id=agent_id, agent_class=agent_class, envelope=env, decision=dec)

def publish_dlq(publisher: DlqPublisher, *, dlq_topic: str, dlq_event: DlqEvent) -> None:
    key = dlq_event.envelope.trace_id or (dlq_event.envelope.message_id or "")
    payload = dlq_event.model_dump()
    value_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    headers = {"x-trace-id": dlq_event.envelope.trace_id}
    publisher.publish(dlq_topic, key=key, value_bytes=value_bytes, headers=headers)
