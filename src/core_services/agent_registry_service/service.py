# -*- coding: utf-8 -*-
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Agent, AgentAudit, AgentClass, AgentStatus
from .validation import validate_phase1_constraints, ValidationError


class ConflictError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
    pass


def _agent_to_dict(a: Agent) -> Dict[str, Any]:
    return {
        "agent_id": a.agent_id,
        "agent_class": a.agent_class.value,
        "agent_version": a.agent_version,
        "public_key_id": a.public_key_id,
        "status": a.status.value,
        "decision_classes": a.decision_classes,
        "channels": a.channels,
        "metadata": a.agent_metadata,
        "version": a.version,
        "created_at": a.created_at.isoformat(),
        "updated_at": a.updated_at.isoformat(),
    }


def register_agent(
    *,
    session: Session,
    agent_id: str,
    agent_class: AgentClass,
    agent_version: str,
    public_key_id: str,
    status: AgentStatus,
    decision_classes: List[str],
    channels: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
    actor: Optional[str],
    trace_id: Optional[str],
) -> Agent:
    validate_phase1_constraints(agent_class, decision_classes, channels)

    existing = session.get(Agent, agent_id)
    if existing is not None:
        raise ConflictError("agent_already_exists")

    now = datetime.utcnow()
    agent = Agent(
        agent_id=agent_id,
        agent_class=agent_class,
        agent_version=agent_version,
        public_key_id=public_key_id,
        status=status,
        decision_classes=list(decision_classes),
        channels=channels,
        metadata=metadata or None,
        version=1,
        created_at=now,
        updated_at=now,
    )
    session.add(agent)

    audit = AgentAudit(
        agent_id=agent_id,
        action="register",
        reason=None,
        before=None,
        after=_agent_to_dict(agent),
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)
    session.flush()
    return agent


def get_agent(session: Session, agent_id: str) -> Agent:
    agent = session.get(Agent, agent_id)
    if agent is None:
        raise NotFoundError("agent_not_found")
    return agent


def list_agents(session: Session, status: Optional[str], agent_class: Optional[str], channel_id: Optional[str]) -> List[Agent]:
    stmt = select(Agent)
    if status:
        stmt = stmt.where(Agent.status == AgentStatus(status))
    if agent_class:
        stmt = stmt.where(Agent.agent_class == AgentClass(agent_class))
    agents = list(session.execute(stmt).scalars().all())
    if channel_id:
        # JSON filtering is DB-specific; we keep it portable by filtering in app for Phase 1.
        agents = [a for a in agents if any(ch.get("channel_id") == channel_id for ch in (a.channels or []))]
    return agents


def update_agent(
    *,
    session: Session,
    agent_id: str,
    if_match_version: int,
    agent_version: str,
    public_key_id: str,
    decision_classes: List[str],
    channels: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]],
    actor: Optional[str],
    trace_id: Optional[str],
) -> Agent:
    agent = get_agent(session, agent_id)
    if agent.version != if_match_version:
        raise ConflictError("version_conflict")

    validate_phase1_constraints(agent.agent_class, decision_classes, channels)

    before = _agent_to_dict(agent)

    agent.agent_version = agent_version
    agent.public_key_id = public_key_id
    agent.decision_classes = list(decision_classes)
    agent.channels = channels
    agent.agent_metadata = metadata or None
    agent.version = agent.version + 1
    agent.updated_at = datetime.utcnow()

    after = _agent_to_dict(agent)
    audit = AgentAudit(
        agent_id=agent_id,
        action="update",
        reason=None,
        before=before,
        after=after,
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)
    session.flush()
    return agent


def change_status(
    *,
    session: Session,
    agent_id: str,
    if_match_version: int,
    status: AgentStatus,
    reason: str,
    actor: Optional[str],
    trace_id: Optional[str],
) -> Agent:
    agent = get_agent(session, agent_id)
    if agent.version != if_match_version:
        raise ConflictError("version_conflict")

    before = _agent_to_dict(agent)

    agent.status = status
    agent.version = agent.version + 1
    agent.updated_at = datetime.utcnow()

    after = _agent_to_dict(agent)
    audit = AgentAudit(
        agent_id=agent_id,
        action="status_change",
        reason=reason,
        before=before,
        after=after,
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)
    session.flush()
    return agent


def revoke_agent(
    *,
    session: Session,
    agent_id: str,
    if_match_version: int,
    actor: Optional[str],
    trace_id: Optional[str],
) -> Agent:
    return change_status(
        session=session,
        agent_id=agent_id,
        if_match_version=if_match_version,
        status=AgentStatus.revoked,
        reason="revoked",
        actor=actor,
        trace_id=trace_id,
    )
