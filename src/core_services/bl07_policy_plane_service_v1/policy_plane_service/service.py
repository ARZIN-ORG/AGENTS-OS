# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Policy, PolicyStatus, Publication, PolicyAudit
from .validation import validate_phase1_policy, normalize_scope_key, ValidationError


class ConflictError(RuntimeError):
    pass


class NotFoundError(RuntimeError):
    pass


def _policy_to_dict(p: Policy) -> Dict[str, Any]:
    return {
        "policy_id": p.policy_id,
        "version": p.version,
        "status": p.status.value,
        "scope": p.scope,
        "constraints": p.constraints,
        "metadata": p.policy_metadata,
        "created_at": p.created_at.isoformat(),
    }


def create_policy(
    *,
    session: Session,
    policy_id: str,
    version: int,
    status: str,
    scope: Dict[str, Any],
    constraints: Dict[str, Any],
    metadata: Optional[Dict[str, Any]],
    actor: Optional[str],
    trace_id: Optional[str],
) -> Policy:
    validate_phase1_policy(scope, constraints)

    existing = session.execute(
        select(Policy).where(Policy.policy_id == policy_id, Policy.version == version)
    ).scalar_one_or_none()
    if existing is not None:
        raise ConflictError("policy_version_already_exists")

    st = PolicyStatus(status) if status else PolicyStatus.draft
    now = datetime.utcnow()

    p = Policy(
        policy_id=policy_id,
        version=version,
        status=st,
        scope=scope,
        constraints=constraints,
        metadata=metadata or None,
        created_at=now,
    )
    session.add(p)

    audit = PolicyAudit(
        policy_id=policy_id,
        action="create",
        reason=None,
        before=None,
        after=_policy_to_dict(p),
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)
    session.flush()
    return p


def list_policies(session: Session, status: Optional[str], policy_id: Optional[str]) -> List[Policy]:
    stmt = select(Policy)
    if status:
        stmt = stmt.where(Policy.status == PolicyStatus(status))
    if policy_id:
        stmt = stmt.where(Policy.policy_id == policy_id)
    return list(session.execute(stmt).scalars().all())


def get_policy_version(session: Session, policy_id: str, version: int) -> Policy:
    p = session.execute(
        select(Policy).where(Policy.policy_id == policy_id, Policy.version == version)
    ).scalar_one_or_none()
    if p is None:
        raise NotFoundError("policy_not_found")
    return p


def publish_policy(
    *,
    session: Session,
    policy_id: str,
    if_match_version: int,
    scope: Dict[str, Any],
    reason: Optional[str],
    actor: Optional[str],
    trace_id: Optional[str],
) -> Publication:
    # ensure policy exists and matches
    p = get_policy_version(session, policy_id, if_match_version)
    validate_phase1_policy(scope, p.constraints)

    scope_key = normalize_scope_key(scope)
    pub = session.execute(select(Publication).where(Publication.scope_key == scope_key, Publication.policy_id == policy_id)).scalar_one_or_none()

    now = datetime.utcnow()
    if pub is None:
        pub = Publication(
            policy_id=policy_id,
            scope_key=scope_key,
            scope=scope,
            active_version=if_match_version,
            previous_version=None,
            note=reason,
            published_at=now,
        )
        session.add(pub)
        before = None
    else:
        before = {
            "policy_id": pub.policy_id,
            "scope_key": pub.scope_key,
            "active_version": pub.active_version,
            "previous_version": pub.previous_version,
            "scope": pub.scope,
        }
        pub.previous_version = pub.active_version
        pub.active_version = if_match_version
        pub.scope = scope
        pub.note = reason
        pub.published_at = now

    audit = PolicyAudit(
        policy_id=policy_id,
        action="publish",
        reason=reason,
        before=before,
        after={
            "policy_id": pub.policy_id,
            "scope": pub.scope,
            "active_version": pub.active_version,
            "previous_version": pub.previous_version,
            "published_at": pub.published_at.isoformat(),
        },
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)

    # mark status active for this version (informational)
    p.status = PolicyStatus.active

    session.flush()
    return pub


def rollback_policy(
    *,
    session: Session,
    policy_id: str,
    scope: Dict[str, Any],
    reason: str,
    actor: Optional[str],
    trace_id: Optional[str],
) -> Publication:
    scope_key = normalize_scope_key(scope)
    pub = session.execute(select(Publication).where(Publication.scope_key == scope_key, Publication.policy_id == policy_id)).scalar_one_or_none()
    if pub is None or pub.previous_version is None:
        raise NotFoundError("no_previous_version")

    before = {
        "active_version": pub.active_version,
        "previous_version": pub.previous_version,
        "scope": pub.scope,
    }
    pub.active_version, pub.previous_version = pub.previous_version, pub.active_version
    pub.note = f"rollback: {reason}"
    pub.published_at = datetime.utcnow()

    audit = PolicyAudit(
        policy_id=policy_id,
        action="rollback",
        reason=reason,
        before=before,
        after={
            "active_version": pub.active_version,
            "previous_version": pub.previous_version,
            "scope": pub.scope,
            "published_at": pub.published_at.isoformat(),
        },
        actor=actor,
        trace_id=trace_id,
    )
    session.add(audit)
    session.flush()
    return pub


def effective_policy(
    *,
    session: Session,
    agent_id: str,
    agent_class: str,
    channel_id: str,
    topic: str,
) -> Dict[str, Any]:
    # Phase 1: lookup by scope_key: agent_class::agent_id::channel_id then fallback agent_class::::channel_id
    def match_topic(scope_topics: List[Dict[str, Any]], topic_val: str) -> bool:
        for r in scope_topics:
            t = r.get("topic", "")
            pat = r.get("pattern", "literal")
            if pat == "literal" and t == topic_val:
                return True
            if pat == "prefix" and topic_val.startswith(t):
                return True
        return False

    keys = [
        f"{agent_class}::{agent_id}::{channel_id}",
        f"{agent_class}::::{channel_id}",
    ]
    pubs = []
    for k in keys:
        pubs.extend(list(session.execute(select(Publication).where(Publication.scope_key == k)).scalars().all()))

    for pub in pubs:
        p = get_policy_version(session, pub.policy_id, pub.active_version)
        scope_topics = (pub.scope or {}).get("topics") or []
        if match_topic(scope_topics, topic):
            return {"policy_id": pub.policy_id, "active_version": pub.active_version, "constraints": p.constraints}

    raise NotFoundError("effective_policy_not_found")
