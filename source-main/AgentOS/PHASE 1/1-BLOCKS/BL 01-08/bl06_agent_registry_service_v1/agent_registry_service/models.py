# -*- coding: utf-8 -*-
from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class AgentStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    revoked = "revoked"


class AgentClass(str, enum.Enum):
    governance = "governance"
    orchestration = "orchestration"
    execution = "execution"
    audit = "audit"
    observer = "observer"
    redteam = "redteam"
    resilience = "resilience"
    management = "management"
    integration = "integration"
    other = "other"


class DecisionClass(str, enum.Enum):
    observe = "observe"
    recommend = "recommend"


class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("agent_id", name="uq_agent_id"),)

    agent_id = Column(String(128), primary_key=True)
    agent_class = Column(Enum(AgentClass, name="agent_class"), nullable=False)
    agent_version = Column(String(64), nullable=False)
    public_key_id = Column(String(128), nullable=False)
    status = Column(Enum(AgentStatus, name="agent_status"), nullable=False, default=AgentStatus.active)

    # Stored as JSON arrays for simplicity and portability.
    decision_classes = Column(JSON, nullable=False)  # list[str]
    channels = Column(JSON, nullable=False)          # list[dict]
    metadata = Column(JSON, nullable=True)

    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())


class AgentAudit(Base):
    __tablename__ = "agent_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(128), nullable=False, index=True)
    action = Column(String(64), nullable=False)
    reason = Column(Text, nullable=True)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)
    actor = Column(String(128), nullable=True)
    trace_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())
