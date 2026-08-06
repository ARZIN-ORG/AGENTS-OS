# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .db import SessionLocal, ENGINE
from .models import Base
from .schemas import SuggestionCreateRequest, SuggestionDecisionRequest, SuggestionEnvelope
from .repo import upsert, get as repo_get, list as repo_list
from .permit_client import PermitClient
from .audit_client import AuditClient
from .publisher import AacpPublisher

APP_NAME = "BL-13 Recommendation Plane (Phase 1) v2"
app = FastAPI(title=APP_NAME, version="0.2.0")

permit = PermitClient()
audit = AuditClient()
publisher = AacpPublisher()

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

@app.post("/v1/suggestions", response_model=SuggestionEnvelope)
def create_suggestion(req: SuggestionCreateRequest, db: Session = Depends(db_dep)) -> SuggestionEnvelope:
    sid = f"sugg_{uuid.uuid4().hex}"
    env = SuggestionEnvelope(
        suggestion_id=sid,
        created_by_agent=req.created_by_agent,
        audience=req.audience,
        title=req.title,
        summary=req.summary,
        domain=req.domain,
        confidence=req.confidence,
        expected_impact=req.expected_impact,
        risk_notes=req.risk_notes,
        proposed_action=req.proposed_action,
    )
    env = upsert(db, env)
    # audit lifecycle
    audit.emit_record({
        "trace_id": sid,
        "message_id": sid,
        "channel_id": "control",
        "topic": "SUGGESTION_CREATED",
        "agent_id": req.created_by_agent,
        "agent_class": "RECOMMENDATION_PLANE",
        "decision": "ALLOW",
        "reason_code": "created",
        "policy_id": "n/a",
        "policy_version": "n/a",
        "signature_valid": True,
        "envelope_hash": "n/a",
        "chain_hash": "n/a",
        "event_time": utc_now(),
    })
    return env

@app.get("/v1/suggestions", response_model=list[SuggestionEnvelope])
def list_suggestions(status: Optional[str] = Query(default=None), db: Session = Depends(db_dep)) -> list[SuggestionEnvelope]:
    return repo_list(db, status=status)

@app.get("/v1/suggestions/{suggestion_id}", response_model=SuggestionEnvelope)
def get_suggestion(suggestion_id: str, db: Session = Depends(db_dep)) -> SuggestionEnvelope:
    env = repo_get(db, suggestion_id)
    if env is None:
        raise HTTPException(status_code=404, detail="not_found")
    return env

@app.post("/v1/suggestions/{suggestion_id}/decision")
def decide(suggestion_id: str, req: SuggestionDecisionRequest, db: Session = Depends(db_dep)) -> Dict[str, Any]:
    env = repo_get(db, suggestion_id)
    if env is None:
        raise HTTPException(status_code=404, detail="not_found")
    if env.status != "PROPOSED":
        raise HTTPException(status_code=409, detail=f"invalid_status:{env.status}")

    env.last_reviewed_by = req.reviewer_id
    env.last_reviewed_at_utc = utc_now()

    if req.decision == "REJECT":
        env.status = "REJECTED"
        env.status_reason = req.reason or "rejected_by_human"
        env = upsert(db, env)
        audit.emit_record({
            "trace_id": suggestion_id,
            "message_id": suggestion_id,
            "channel_id": "control",
            "topic": "SUGGESTION_REJECTED",
            "agent_id": req.reviewer_id,
            "agent_class": "HUMAN",
            "decision": "DENY",
            "reason_code": env.status_reason or "rejected",
            "policy_id": "n/a",
            "policy_version": "n/a",
            "signature_valid": True,
            "envelope_hash": "n/a",
            "chain_hash": "n/a",
            "event_time": utc_now(),
        })
        return {"suggestion": env.model_dump(), "permit_decision": {"decision": "DENY"}, "publish": {"published": False}}

    if req.decision == "MODIFY":
        if req.title:
            env.title = req.title
        if req.summary:
            env.summary = req.summary
        if req.proposed_action is not None:
            env.proposed_action = req.proposed_action
        env.status_reason = req.reason or "modified_by_human"
        env = upsert(db, env)
        audit.emit_record({
            "trace_id": suggestion_id,
            "message_id": suggestion_id,
            "channel_id": "control",
            "topic": "SUGGESTION_REVIEWED",
            "agent_id": req.reviewer_id,
            "agent_class": "HUMAN",
            "decision": "ALLOW",
            "reason_code": "modified_pending_accept",
            "policy_id": "n/a",
            "policy_version": "n/a",
            "signature_valid": True,
            "envelope_hash": "n/a",
            "chain_hash": "n/a",
            "event_time": utc_now(),
        })
        return {"suggestion": env.model_dump(), "permit_decision": {"decision": "DENY", "reason": "modified_pending_accept"}, "publish": {"published": False}}

    # ACCEPT => Permit => publish exec request (optional)
    exec_request = {
        "kind": "EXECUTION_REQUEST",
        "source": "BL13_RECOMMENDATION_PLANE",
        "suggestion_id": env.suggestion_id,
        "requested_by": req.reviewer_id,
        "requested_at_utc": utc_now(),
        "proposed_action": env.proposed_action,
        "intent": {
            "title": env.title,
            "summary": env.summary,
            "domain": env.domain,
            "confidence": env.confidence,
        },
    }

    permit_decision = permit.request_permit(exec_request).model_dump()

    if permit_decision.get("decision") != "ALLOW":
        env.status = "REJECTED"
        env.status_reason = f"permit:{permit_decision.get('reason', 'deny')}"
        env = upsert(db, env)
        audit.emit_record({
            "trace_id": suggestion_id,
            "message_id": suggestion_id,
            "channel_id": "control",
            "topic": "SUGGESTION_REJECTED",
            "agent_id": req.reviewer_id,
            "agent_class": "HUMAN",
            "decision": "DENY",
            "reason_code": env.status_reason or "permit_deny",
            "policy_id": "n/a",
            "policy_version": "n/a",
            "signature_valid": True,
            "envelope_hash": "n/a",
            "chain_hash": "n/a",
            "event_time": utc_now(),
        })
        return {"suggestion": env.model_dump(), "permit_decision": permit_decision, "publish": {"published": False, "mode": "fail_closed"}}

    env.status = "ACCEPTED"
    env.human_final_approval_id = permit_decision.get("permit_id")
    env = upsert(db, env)

    publish_meta = publisher.publish_exec_request(exec_request)

    audit.emit_record({
        "trace_id": suggestion_id,
        "message_id": suggestion_id,
        "channel_id": "control",
        "topic": "SUGGESTION_ACCEPTED",
        "agent_id": req.reviewer_id,
        "agent_class": "HUMAN",
        "decision": "ALLOW",
        "reason_code": "permit_allow",
        "policy_id": "n/a",
        "policy_version": "n/a",
        "signature_valid": True,
        "envelope_hash": "n/a",
        "chain_hash": "n/a",
        "event_time": utc_now(),
    })

    return {"suggestion": env.model_dump(), "permit_decision": permit_decision, "publish": publish_meta}
