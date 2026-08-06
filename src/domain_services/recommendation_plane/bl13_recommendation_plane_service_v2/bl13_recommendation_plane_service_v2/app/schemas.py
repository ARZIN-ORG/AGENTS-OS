# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

SuggestionStatus = Literal["PROPOSED", "REJECTED", "ACCEPTED", "SUPERSEDED"]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class SuggestionEnvelope(BaseModel):
    suggestion_id: str = Field(..., min_length=8, max_length=128)
    created_at_utc: str = Field(default_factory=utc_now)
    created_by_agent: str = Field(..., min_length=3, max_length=128)
    audience: Literal["MANAGER", "USER", "OPS"] = "MANAGER"

    title: str = Field(..., min_length=3, max_length=200)
    summary: str = Field(..., min_length=3, max_length=2000)
    domain: str = Field(..., min_length=2, max_length=64)
    confidence: float = Field(..., ge=0.0, le=1.0)

    expected_impact: Dict[str, Any] = Field(default_factory=dict)
    risk_notes: List[str] = Field(default_factory=list)
    proposed_action: Dict[str, Any] = Field(default_factory=dict)

    status: SuggestionStatus = "PROPOSED"
    status_reason: Optional[str] = Field(default=None, max_length=500)

    last_reviewed_by: Optional[str] = None
    last_reviewed_at_utc: Optional[str] = None
    human_final_approval_id: Optional[str] = None

    @field_validator("risk_notes")
    @classmethod
    def _limit_risk_notes(cls, v: List[str]) -> List[str]:
        if len(v) > 50:
            raise ValueError("risk_notes too large (max 50)")
        for s in v:
            if len(s) > 300:
                raise ValueError("risk_notes item too long (max 300 chars)")
        return v

class SuggestionCreateRequest(BaseModel):
    created_by_agent: str
    audience: Literal["MANAGER", "USER", "OPS"] = "MANAGER"
    title: str
    summary: str
    domain: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    expected_impact: Dict[str, Any] = Field(default_factory=dict)
    risk_notes: List[str] = Field(default_factory=list)
    proposed_action: Dict[str, Any] = Field(default_factory=dict)

class SuggestionDecisionRequest(BaseModel):
    reviewer_id: str = Field(..., min_length=3, max_length=128)
    decision: Literal["ACCEPT", "REJECT", "MODIFY"]
    title: Optional[str] = None
    summary: Optional[str] = None
    proposed_action: Optional[Dict[str, Any]] = None
    reason: Optional[str] = Field(default=None, max_length=500)

class PermitDecision(BaseModel):
    permit_id: str
    decision: Literal["ALLOW", "DENY"]
    reason: Optional[str] = None
    trace_id: Optional[str] = None
