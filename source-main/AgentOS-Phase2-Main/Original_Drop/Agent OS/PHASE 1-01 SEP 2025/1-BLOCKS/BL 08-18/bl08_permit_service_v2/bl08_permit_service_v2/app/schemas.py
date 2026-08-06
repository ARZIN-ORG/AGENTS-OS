# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

Decision = Literal["ALLOW", "DENY"]

class ExecutionRequest(BaseModel):
    kind: Literal["EXECUTION_REQUEST"]
    source: str = Field(..., min_length=2, max_length=128)

    requested_by: str = Field(..., min_length=3, max_length=128)
    requested_at_utc: str = Field(..., min_length=10, max_length=64)

    action_type: str = Field(..., min_length=2, max_length=128)
    channel: Literal["VOICE", "TEXT", "CONTROL"] = "CONTROL"
    scope: Optional[str] = Field(default=None, max_length=128)

    request_id: Optional[str] = Field(default=None, max_length=128)

    target: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)

class PermitDecision(BaseModel):
    permit_id: str
    decision: Decision
    reason: Optional[str] = None
    trace_id: Optional[str] = None
