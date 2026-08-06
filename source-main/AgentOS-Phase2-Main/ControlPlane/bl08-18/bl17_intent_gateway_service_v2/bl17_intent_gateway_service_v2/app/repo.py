# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from .models import IntentRow
from .schemas import IntentDraft

def row_to_draft(r: IntentRow) -> IntentDraft:
    return IntentDraft(
        intent_id=r.intent_id,
        created_at_utc=r.created_at_utc,
        actor_id=r.actor_id,
        channel=r.channel,  # type: ignore
        original_input=r.original_input,
        action_type=r.action_type,
        target=json.loads(r.target_json or "{}"),
        parameters=json.loads(r.parameters_json or "{}"),
        rationale=r.rationale,
        status=r.status,  # type: ignore
        reviewed_by=r.reviewed_by,
        reviewed_at_utc=r.reviewed_at_utc,
        finalized_by=r.finalized_by,
        finalized_at_utc=r.finalized_at_utc,
        final_approval_id=r.final_approval_id,
        trace_id=r.trace_id,
    )

def upsert(db: Session, d: IntentDraft) -> IntentDraft:
    r = db.get(IntentRow, d.intent_id)
    if r is None:
        r = IntentRow(intent_id=d.intent_id)
        db.add(r)

    r.created_at_utc = d.created_at_utc
    r.actor_id = d.actor_id
    r.channel = d.channel
    r.original_input = d.original_input
    r.action_type = d.action_type
    r.target_json = json.dumps(d.target, ensure_ascii=False)
    r.parameters_json = json.dumps(d.parameters, ensure_ascii=False)
    r.rationale = d.rationale
    r.status = d.status
    r.reviewed_by = d.reviewed_by
    r.reviewed_at_utc = d.reviewed_at_utc
    r.finalized_by = d.finalized_by
    r.finalized_at_utc = d.finalized_at_utc
    r.final_approval_id = d.final_approval_id
    r.trace_id = d.trace_id

    db.commit()
    db.refresh(r)
    return row_to_draft(r)

def get(db: Session, intent_id: str) -> Optional[IntentDraft]:
    r = db.get(IntentRow, intent_id)
    return None if r is None else row_to_draft(r)

def list(db: Session) -> List[IntentDraft]:
    rows = db.execute(select(IntentRow)).scalars().all()
    out = [row_to_draft(r) for r in rows]
    out.sort(key=lambda x: x.created_at_utc, reverse=True)
    return out
