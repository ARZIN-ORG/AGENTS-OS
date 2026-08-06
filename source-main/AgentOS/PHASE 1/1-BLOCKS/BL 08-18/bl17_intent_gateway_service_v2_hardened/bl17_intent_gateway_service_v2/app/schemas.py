# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

IntentStatus = Literal["DRAFT", "FINALIZED", "REJECTED"]

class TextIntentIn(BaseModel):
    actor_id: str = Field(..., min_length=3, max_length=128)
    text: str = Field(..., min_length=1, max_length=4000)

class VoiceIntentIn(BaseModel):
    actor_id: str = Field(..., min_length=3, max_length=128)
    transcript_text: str = Field(..., min_length=1, max_length=4000)

class IntentDraft(BaseModel):
    intent_id: str
    created_at_utc: str
    actor_id: str
    channel: Literal["VOICE", "TEXT"]
    original_input: str
    action_type: str
    target: Dict[str, Any] = {}
    parameters: Dict[str, Any] = {}
    rationale: Optional[str] = None
    status: IntentStatus = "DRAFT"
    reviewed_by: Optional[str] = None
    reviewed_at_utc: Optional[str] = None
    finalized_by: Optional[str] = None
    finalized_at_utc: Optional[str] = None
    final_approval_id: Optional[str] = None
    trace_id: Optional[str] = None

class ReviewEditIn(BaseModel):
    reviewer_id: str = Field(..., min_length=3, max_length=128)
    action_type: Optional[str] = None
    target: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    rationale: Optional[str] = Field(default=None, max_length=1000)

class FinalizeIn(BaseModel):
    approver_id: str = Field(..., min_length=3, max_length=128)
