# -*- coding: utf-8 -*-
from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, JSON, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PolicyStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    deprecated = "deprecated"


class Policy(Base):
    __tablename__ = "policies"
    __table_args__ = (UniqueConstraint("policy_id", "version", name="uq_policy_version"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), nullable=False)
    version = Column(Integer, nullable=False)
    status = Column(Enum(PolicyStatus, name="policy_status"), nullable=False, default=PolicyStatus.draft)

    scope = Column(JSON, nullable=False)
    constraints = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())


class Publication(Base):
    __tablename__ = "policy_publications"
    __table_args__ = (
        Index("ix_pub_scope_key", "scope_key"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), nullable=False)
    scope_key = Column(String(256), nullable=False)  # normalized scope to lookup fast
    scope = Column(JSON, nullable=False)

    active_version = Column(Integer, nullable=False)
    previous_version = Column(Integer, nullable=True)

    note = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())


class PolicyAudit(Base):
    __tablename__ = "policy_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    policy_id = Column(String(128), nullable=False)
    action = Column(String(64), nullable=False)
    reason = Column(Text, nullable=True)
    before = Column(JSON, nullable=True)
    after = Column(JSON, nullable=True)
    actor = Column(String(128), nullable=True)
    trace_id = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.utcnow())
