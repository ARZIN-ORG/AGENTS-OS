# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

class HealthOut(BaseModel):
    ok: bool
    service: str
    upstream: Dict[str, Any] = Field(default_factory=dict)

class AuditEvent(BaseModel):
    # Console treats these as opaque; only uses fields if present.
    ts_utc: Optional[str] = None
    trace_id: Optional[str] = None
    event_type: Optional[str] = None
    actor_id: Optional[str] = None
    action_type: Optional[str] = None
    channel: Optional[str] = None
    decision: Optional[str] = None
    prev_hash: Optional[str] = None
    chain_hash: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

class TimelineOut(BaseModel):
    window_hours: int
    count: int
    events: List[AuditEvent]

class KPIOut(BaseModel):
    window_hours: int
    total: int
    allow: int
    deny: int
    by_channel: Dict[str, int] = Field(default_factory=dict)
    by_action: Dict[str, int] = Field(default_factory=dict)

class ChainVerifyOut(BaseModel):
    window_hours: int
    checked: int
    ok: bool
    broken_at_index: Optional[int] = None
    reason: Optional[str] = None
