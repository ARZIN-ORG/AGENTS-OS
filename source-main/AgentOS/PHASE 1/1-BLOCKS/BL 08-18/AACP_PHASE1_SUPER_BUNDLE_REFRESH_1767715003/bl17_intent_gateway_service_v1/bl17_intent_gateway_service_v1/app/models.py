# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

IntentStatus = Literal["DRAFT", "FINALIZED", "REJECTED"]

class TextIntentIn(BaseModel):
    actor_id: str = Field(..., min_length=3, max_length=128)  # manager/user id (post-MFA)
    text: str = Field(..., min_length=1, max_length=4000)
    channel: Literal["TEXT"] = "TEXT"

class VoiceIntentIn(BaseModel):
    actor_id: str = Field(..., min_length=3, max_length=128)
    transcript_text: str = Field(..., min_length=1, max_length=4000)
    channel: Literal["VOICE"] = "VOICE"

class IntentDraft(BaseModel):
    intent_id: str = Field(..., min_length=8, max_length=128)
    created_at_utc: str = Field(default_factory=utc_now)
    actor_id: str
    channel: Literal["VOICE", "TEXT"]

    # Human readable
    original_input: str = Field(..., min_length=1, max_length=4000)

    # Structured interpretation (editable by human)
    action_type: str = Field(..., min_length=1, max_length=128)
    target: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rationale: Optional[str] = Field(default=None, max_length=1000)

    status: IntentStatus = "DRAFT"
    reviewed_by: Optional[str] = None
    reviewed_at_utc: Optional[str] = None

    finalized_by: Optional[str] = None
    finalized_at_utc: Optional[str] = None
    final_approval_id: Optional[str] = None  # permit_id
    trace_id: Optional[str] = None

class ReviewEditIn(BaseModel):
    reviewer_id: str = Field(..., min_length=3, max_length=128)
    action_type: Optional[str] = None
    target: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    rationale: Optional[str] = Field(default=None, max_length=1000)

class FinalizeIn(BaseModel):
    approver_id: str = Field(..., min_length=3, max_length=128)
    # optional extra confirmation token handled by UI; not enforced here in phase-1
    confirm_token: Optional[str] = None

class PermitDecision(BaseModel):
    permit_id: str
    decision: Literal["ALLOW", "DENY"]
    reason: Optional[str] = None
    trace_id: Optional[str] = None
