# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TopicRule(BaseModel):
    topic: str
    pattern: str = Field(default="literal", pattern="^(literal|prefix)$")


class PolicyScope(BaseModel):
    agent_class: str
    agent_id: Optional[str] = None
    channel_id: str
    topics: List[TopicRule]


class PolicyConstraints(BaseModel):
    decision_classes: List[str]
    signature_required: bool
    max_payload_bytes: int = 1048576
    ttl_seconds_min: int = 1
    ttl_seconds_max: int = 300


class PolicyCreate(BaseModel):
    policy_id: str
    version: int
    status: str = "draft"
    scope: PolicyScope
    constraints: PolicyConstraints
    metadata: Optional[Dict[str, Any]] = None


class PolicyOut(BaseModel):
    policy_id: str
    version: int
    status: str
    scope: PolicyScope
    constraints: PolicyConstraints
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class PolicyPublish(BaseModel):
    scope: PolicyScope
    reason: Optional[str] = None


class PolicyRollback(BaseModel):
    scope: PolicyScope
    reason: str


class PublicationOut(BaseModel):
    policy_id: str
    active_version: int
    scope: PolicyScope
    published_at: datetime
    note: Optional[str] = None


class EffectivePolicy(BaseModel):
    policy_id: str
    active_version: int
    constraints: PolicyConstraints
