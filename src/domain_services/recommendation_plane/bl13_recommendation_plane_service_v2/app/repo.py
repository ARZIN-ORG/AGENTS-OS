# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import SuggestionRow
from .schemas import SuggestionEnvelope

def row_to_env(row: SuggestionRow) -> SuggestionEnvelope:
    return SuggestionEnvelope(
        suggestion_id=row.suggestion_id,
        created_at_utc=row.created_at_utc,
        created_by_agent=row.created_by_agent,
        audience=row.audience,  # type: ignore
        title=row.title,
        summary=row.summary,
        domain=row.domain,
        confidence=float(row.confidence),
        expected_impact=json.loads(row.expected_impact_json or "{}"),
        risk_notes=json.loads(row.risk_notes_json or "[]"),
        proposed_action=json.loads(row.proposed_action_json or "{}"),
        status=row.status,  # type: ignore
        status_reason=row.status_reason,
        last_reviewed_by=row.last_reviewed_by,
        last_reviewed_at_utc=row.last_reviewed_at_utc,
        human_final_approval_id=row.human_final_approval_id,
    )

def upsert(db: Session, env: SuggestionEnvelope) -> SuggestionEnvelope:
    row = db.get(SuggestionRow, env.suggestion_id)
    if row is None:
        row = SuggestionRow(suggestion_id=env.suggestion_id)
        db.add(row)

    row.created_at_utc = env.created_at_utc
    row.created_by_agent = env.created_by_agent
    row.audience = env.audience
    row.title = env.title
    row.summary = env.summary
    row.domain = env.domain
    row.confidence = float(env.confidence)
    row.expected_impact_json = json.dumps(env.expected_impact, ensure_ascii=False)
    row.risk_notes_json = json.dumps(env.risk_notes, ensure_ascii=False)
    row.proposed_action_json = json.dumps(env.proposed_action, ensure_ascii=False)
    row.status = env.status
    row.status_reason = env.status_reason
    row.last_reviewed_by = env.last_reviewed_by
    row.last_reviewed_at_utc = env.last_reviewed_at_utc
    row.human_final_approval_id = env.human_final_approval_id

    db.commit()
    db.refresh(row)
    return row_to_env(row)

def get(db: Session, suggestion_id: str) -> Optional[SuggestionEnvelope]:
    row = db.get(SuggestionRow, suggestion_id)
    return None if row is None else row_to_env(row)

def list(db: Session, status: Optional[str] = None) -> List[SuggestionEnvelope]:
    stmt = select(SuggestionRow)
    if status:
        stmt = stmt.where(SuggestionRow.status == status)
    rows = db.execute(stmt).scalars().all()
    envs = [row_to_env(r) for r in rows]
    envs.sort(key=lambda x: x.created_at_utc, reverse=True)
    return envs
