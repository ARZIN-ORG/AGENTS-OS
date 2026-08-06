from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

class AacpAuditRecordIn(BaseModel):
    trace_id: str
    message_id: str | None = None

    channel_id: str
    topic: str

    agent_id: str
    agent_class: str

    decision: str = Field(..., pattern="^(ALLOW|DENY)$")
    reason_code: str

    policy_id: str | None = None
    policy_version: int | None = None

    signature_valid: bool = False

    envelope_hash: str | None = None
    chain_hash: str | None = None

    event_time: datetime | None = None

    raw: dict | None = None

class AacpAuditRecordOut(BaseModel):
    id: int
    trace_id: str
    message_id: str | None
    channel_id: str
    topic: str
    agent_id: str
    agent_class: str
    decision: str
    reason_code: str
    policy_id: str | None
    policy_version: int | None
    signature_valid: bool
    envelope_hash: str | None
    chain_hash: str | None
    event_time: datetime
    received_time: datetime
