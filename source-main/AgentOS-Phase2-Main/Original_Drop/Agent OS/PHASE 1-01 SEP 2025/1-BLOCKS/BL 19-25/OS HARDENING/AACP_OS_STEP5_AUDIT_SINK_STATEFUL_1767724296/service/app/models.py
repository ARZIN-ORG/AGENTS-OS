from __future__ import annotations
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field

class AppendRequest(BaseModel):
    envelope: Dict[str, Any] = Field(..., description="AuditEnvelope fields")
    payload_digest: Optional[str] = Field(None, description="sha256 hex of payload canonical json")
    prev_chain_hash: Optional[str] = Field(None, description="previous chain hash from caller (optional)")

class AppendResponse(BaseModel):
    ok: bool
    id: str
    seq: int
    chain_hash: str
    prev_chain_hash: Optional[str]
    ts_ms: int

class RecordOut(BaseModel):
    id: str
    seq: int
    ts_ms: int
    trace_id: str
    event_id: str
    channel_id: str
    topic: str
    producer_id: str
    consumer_id: str
    policy_id: str
    policy_version: str
    permit_id: str
    intent_id: str
    payload_digest: Optional[str]
    prev_chain_hash: Optional[str]
    chain_hash: str
    envelope: Dict[str, Any]
