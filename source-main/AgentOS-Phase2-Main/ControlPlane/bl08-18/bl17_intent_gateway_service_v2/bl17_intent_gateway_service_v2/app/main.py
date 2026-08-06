# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .db import SessionLocal, ENGINE
from .models import Base
from .schemas import IntentDraft, TextIntentIn, VoiceIntentIn, ReviewEditIn, FinalizeIn
from .intent_parser import parse_intent
from .repo import upsert, get as repo_get, list as repo_list
from .permit_client import PermitClient
from .aacp_publish import AacpPublisher
from .recommendation_client import RecommendationClient

APP_NAME = "BL-17 Omni-Channel Intent Gateway (Phase 1) v2"
app = FastAPI(title=APP_NAME, version="0.2.0")

permit = PermitClient()
publisher = AacpPublisher()
reco = RecommendationClient()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def db_dep():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=ENGINE)

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": APP_NAME}

@app.post("/v1/intents/text", response_model=IntentDraft)
def create_text(inp: TextIntentIn, db: Session = Depends(db_dep)) -> IntentDraft:
    action_type, target, params = parse_intent(inp.text)
    iid = f"intent_{uuid.uuid4().hex}"
    draft = IntentDraft(
        intent_id=iid,
        created_at_utc=utc_now(),
        actor_id=inp.actor_id,
        channel="TEXT",
        original_input=inp.text,
        action_type=action_type,
        target=target,
        parameters=params,
        rationale=None,
        status="DRAFT",
    )
    return upsert(db, draft)

@app.post("/v1/intents/voice", response_model=IntentDraft)
def create_voice(inp: VoiceIntentIn, db: Session = Depends(db_dep)) -> IntentDraft:
    action_type, target, params = parse_intent(inp.transcript_text)
    iid = f"intent_{uuid.uuid4().hex}"
    draft = IntentDraft(
        intent_id=iid,
        created_at_utc=utc_now(),
        actor_id=inp.actor_id,
        channel="VOICE",
        original_input=inp.transcript_text,
        action_type=action_type,
        target=target,
        parameters=params,
        rationale=None,
        status="DRAFT",
    )
    return upsert(db, draft)

@app.get("/v1/intents", response_model=list[IntentDraft])
def list_intents(db: Session = Depends(db_dep)) -> list[IntentDraft]:
    return repo_list(db)

@app.get("/v1/intents/{intent_id}", response_model=IntentDraft)
def get_intent(intent_id: str, db: Session = Depends(db_dep)) -> IntentDraft:
    d = repo_get(db, intent_id)
    if d is None:
        raise HTTPException(status_code=404, detail="not_found")
    return d

@app.post("/v1/intents/{intent_id}/review", response_model=IntentDraft)
def review(intent_id: str, inp: ReviewEditIn, db: Session = Depends(db_dep)) -> IntentDraft:
    d = repo_get(db, intent_id)
    if d is None:
        raise HTTPException(status_code=404, detail="not_found")
    if d.status != "DRAFT":
        raise HTTPException(status_code=409, detail=f"invalid_status:{d.status}")

    d.reviewed_by = inp.reviewer_id
    d.reviewed_at_utc = utc_now()
    if inp.action_type:
        d.action_type = inp.action_type
    if inp.target is not None:
        d.target = inp.target
    if inp.parameters is not None:
        d.parameters = inp.parameters
    if inp.rationale is not None:
        d.rationale = inp.rationale
    return upsert(db, d)

@app.post("/v1/intents/{intent_id}/finalize")
def finalize(intent_id: str, inp: FinalizeIn, db: Session = Depends(db_dep)) -> Dict[str, Any]:
    d = repo_get(db, intent_id)
    if d is None:
        raise HTTPException(status_code=404, detail="not_found")
    if d.status != "DRAFT":
        raise HTTPException(status_code=409, detail=f"invalid_status:{d.status}")

    exec_request = {
        "kind": "EXECUTION_REQUEST",
        "source": "BL17_INTENT_GATEWAY",
        "intent_id": d.intent_id,
        "requested_by": inp.approver_id,
        "requested_at_utc": utc_now(),
        "action_type": d.action_type,
        "target": d.target,
        "parameters": d.parameters,
        "channel": d.channel,
        "original_input": d.original_input,
    }

    permit_decision = permit.request_permit(exec_request).model_dump()

    if permit_decision.get("decision") != "ALLOW":
        d.status = "REJECTED"
        d.finalized_by = inp.approver_id
        d.finalized_at_utc = utc_now()
        d.final_approval_id = permit_decision.get("permit_id")
        d.trace_id = permit_decision.get("trace_id")
        upsert(db, d)
        return {"intent": d.model_dump(), "permit_decision": permit_decision, "publish": {"published": False, "mode": "fail_closed"}}

    d.status = "FINALIZED"
    d.finalized_by = inp.approver_id
    d.finalized_at_utc = utc_now()
    d.final_approval_id = permit_decision.get("permit_id")
    d.trace_id = permit_decision.get("trace_id")
    upsert(db, d)

    publish_meta = publisher.publish_exec_request(exec_request)
    return {"intent": d.model_dump(), "permit_decision": permit_decision, "publish": publish_meta}

# BL-13 proxy
@app.get("/v1/suggestions")
def list_suggestions(status: Optional[str] = Query(default=None)) -> Any:
    return reco.list_suggestions(status=status)

@app.get("/v1/suggestions/{suggestion_id}")
def get_suggestion(suggestion_id: str) -> Any:
    return reco.get_suggestion(suggestion_id)

@app.post("/v1/suggestions/{suggestion_id}/decision")
def decide_suggestion(suggestion_id: str, payload: Dict[str, Any]) -> Any:
    return reco.decide(suggestion_id, payload)
