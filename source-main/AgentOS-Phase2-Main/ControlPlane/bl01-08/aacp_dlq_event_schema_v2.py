# -*- coding: utf-8 -*-
"""
ARZIN / AACP — DLQ Event Schema v2 (Phase-1)
File: aacp_dlq_event_schema_v2.py

Purpose:
- Standard, reconstructable DLQ payload for DENY/FAIL-CLOSED events.
- Designed for auditability and regulator-grade traceability.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pydantic import BaseModel, Field

class DlqEnvelope(BaseModel):
    trace_id: str
    message_id: str | None = None
    channel_id: str
    topic: str
    payload_bytes: int
    ttl_seconds: int
    signature_valid: bool
    chain_hash: str | None = None
    envelope_hash: str | None = None

class DlqDecision(BaseModel):
    decision: str = Field(..., pattern="^(DENY)$")
    reason_code: str
    policy_id: str | None = None
    policy_version: int | None = None
    gate: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DlqEvent(BaseModel):
    agent_id: str
    agent_class: str
    envelope: DlqEnvelope
    decision: DlqDecision
    raw_headers: dict | None = None
    raw_payload_ref: str | None = None
