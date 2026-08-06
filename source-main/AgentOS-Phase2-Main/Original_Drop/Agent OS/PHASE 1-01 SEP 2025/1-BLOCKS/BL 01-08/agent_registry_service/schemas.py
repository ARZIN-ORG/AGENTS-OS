# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .models import AgentClass, AgentStatus


class TopicRule(BaseModel):
    topic: str
    pattern: str = Field(default="literal", pattern="^(literal|prefix)$")


class ChannelAllowlist(BaseModel):
    channel_id: str
    topics: List[TopicRule]


class AgentCreate(BaseModel):
    agent_id: str
    agent_class: AgentClass
    agent_version: str
    public_key_id: str
    status: AgentStatus = AgentStatus.active
    decision_classes: List[str]
    channels: List[ChannelAllowlist]
    metadata: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    agent_version: str
    public_key_id: str
    decision_classes: List[str]
    channels: List[ChannelAllowlist]
    metadata: Optional[Dict[str, Any]] = None


class AgentStatusChange(BaseModel):
    status: AgentStatus
    reason: str


class AgentOut(BaseModel):
    agent_id: str
    agent_class: AgentClass
    agent_version: str
    public_key_id: str
    status: AgentStatus
    decision_classes: List[str]
    channels: List[ChannelAllowlist]
    metadata: Optional[Dict[str, Any]] = None
    version: int
    created_at: datetime
    updated_at: datetime


class EffectiveAllowlist(BaseModel):
    agent_id: str
    status: AgentStatus
    version: int
    decision_classes: List[str]
    channels: List[ChannelAllowlist]
