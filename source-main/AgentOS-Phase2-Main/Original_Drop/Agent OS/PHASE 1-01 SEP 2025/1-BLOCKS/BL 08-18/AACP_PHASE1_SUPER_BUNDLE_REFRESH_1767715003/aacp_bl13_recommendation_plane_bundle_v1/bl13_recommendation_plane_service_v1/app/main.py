# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .models import SuggestionCreateRequest, SuggestionDecisionRequest, SuggestionEnvelope
from .store import InMemorySuggestionStore
from .permit_client import PermitClient
from .aacp_publish import AacpPublisher

APP_NAME = "BL-13 Recommendation Plane (Phase 1)"
app = FastAPI(title=APP_NAME, version="0.1.0")

store = InMemorySuggestionStore()
permit = PermitClient()
publisher = AacpPublisher()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class DecisionResponse(BaseModel):
    suggestion: SuggestionEnvelope
    permit_decision: Dict[str, Any]
    publish: Dict[str, Any]

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": APP_NAME}

@app.post("/v1/suggestions", response_model=SuggestionEnvelope)
def create_suggestion(req: SuggestionCreateRequest) -> SuggestionEnvelope:
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
    return store.upsert(env)

@app.get("/v1/suggestions", response_model=list[SuggestionEnvelope])
def list_suggestions(status: Optional[str] = Query(default=None)) -> list[SuggestionEnvelope]:
    return store.list(status=status)

@app.get("/v1/suggestions/{suggestion_id}", response_model=SuggestionEnvelope)
def get_suggestion(suggestion_id: str) -> SuggestionEnvelope:
    env = store.get(suggestion_id)
    if env is None:
        raise HTTPException(status_code=404, detail="not_found")
    return env

@app.post("/v1/suggestions/{suggestion_id}/decision", response_model=DecisionResponse)
def decide(suggestion_id: str, req: SuggestionDecisionRequest) -> DecisionResponse:
    env = store.get(suggestion_id)
    if env is None:
        raise HTTPException(status_code=404, detail="not_found")
    if env.status != "PROPOSED":
        raise HTTPException(status_code=409, detail=f"invalid_status:{env.status}")

    env.last_reviewed_by = req.reviewer_id
    env.last_reviewed_at_utc = utc_now()

    if req.decision == "REJECT":
        env.status = "REJECTED"
        env.status_reason = req.reason or "rejected_by_human"
        store.upsert(env)
        return DecisionResponse(
            suggestion=env,
            permit_decision={"decision": "DENY", "reason": "human_reject"},
            publish={"published": False},
        )

    if req.decision == "MODIFY":
        if req.title:
            env.title = req.title
        if req.summary:
            env.summary = req.summary
        if req.proposed_action is not None:
            env.proposed_action = req.proposed_action
        env.status_reason = req.reason or "modified_by_human"
        store.upsert(env)
        return DecisionResponse(
            suggestion=env,
            permit_decision={"decision": "DENY", "reason": "modified_pending_accept"},
            publish={"published": False},
        )

    # ACCEPT: request execution via Permit Service (no direct execution here).
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
        store.upsert(env)
        return DecisionResponse(
            suggestion=env,
            permit_decision=permit_decision,
            publish={"published": False, "mode": "fail_closed"},
        )

    env.status = "ACCEPTED"
    env.human_final_approval_id = permit_decision.get("permit_id")
    store.upsert(env)

    publish_meta = publisher.publish_exec_request(exec_request)
    return DecisionResponse(suggestion=env, permit_decision=permit_decision, publish=publish_meta)
