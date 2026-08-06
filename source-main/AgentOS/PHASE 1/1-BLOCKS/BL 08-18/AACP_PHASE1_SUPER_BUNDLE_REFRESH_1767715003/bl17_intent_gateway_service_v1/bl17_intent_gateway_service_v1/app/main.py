# -*- coding: utf-8 -*-
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .models import (
    IntentDraft,
    TextIntentIn,
    VoiceIntentIn,
    ReviewEditIn,
    FinalizeIn,
)
from .store import InMemoryIntentStore
from .intent_parser import parse_intent
from .permit_client import PermitClient
from .aacp_publish import AacpPublisher
from .recommendation_client import RecommendationClient

APP_NAME = "BL-17 Omni-Channel Intent Gateway (Phase 1)"
app = FastAPI(title=APP_NAME, version="0.1.0")

store = InMemoryIntentStore()
permit = PermitClient()
publisher = AacpPublisher()
reco = RecommendationClient()

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class FinalizeResponse(BaseModel):
    intent: IntentDraft
    permit_decision: Dict[str, Any]
    publish: Dict[str, Any]

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": APP_NAME}

@app.post("/v1/intents/text", response_model=IntentDraft)
def create_intent_text(inp: TextIntentIn) -> IntentDraft:
    action_type, target, params = parse_intent(inp.text)
    intent_id = f"intent_{uuid.uuid4().hex}"
    draft = IntentDraft(
        intent_id=intent_id,
        actor_id=inp.actor_id,
        channel="TEXT",
        original_input=inp.text,
        action_type=action_type,
        target=target,
        parameters=params,
        rationale=None,
    )
    return store.upsert(draft)

@app.post("/v1/intents/voice", response_model=IntentDraft)
def create_intent_voice(inp: VoiceIntentIn) -> IntentDraft:
    # Voice is represented as a transcript in Phase-1. ASR integration is external.
    action_type, target, params = parse_intent(inp.transcript_text)
    intent_id = f"intent_{uuid.uuid4().hex}"
    draft = IntentDraft(
        intent_id=intent_id,
        actor_id=inp.actor_id,
        channel="VOICE",
        original_input=inp.transcript_text,
        action_type=action_type,
        target=target,
        parameters=params,
        rationale=None,
    )
    return store.upsert(draft)

@app.get("/v1/intents", response_model=list[IntentDraft])
def list_intents() -> list[IntentDraft]:
    return store.list()

@app.get("/v1/intents/{intent_id}", response_model=IntentDraft)
def get_intent(intent_id: str) -> IntentDraft:
    item = store.get(intent_id)
    if item is None:
        raise HTTPException(status_code=404, detail="not_found")
    return item

@app.post("/v1/intents/{intent_id}/review", response_model=IntentDraft)
def review_edit(intent_id: str, inp: ReviewEditIn) -> IntentDraft:
    item = store.get(intent_id)
    if item is None:
        raise HTTPException(status_code=404, detail="not_found")
    if item.status != "DRAFT":
        raise HTTPException(status_code=409, detail=f"invalid_status:{item.status}")

    item.reviewed_by = inp.reviewer_id
    item.reviewed_at_utc = utc_now()
    if inp.action_type:
        item.action_type = inp.action_type
    if inp.target is not None:
        item.target = inp.target
    if inp.parameters is not None:
        item.parameters = inp.parameters
    if inp.rationale is not None:
        item.rationale = inp.rationale
    return store.upsert(item)

@app.post("/v1/intents/{intent_id}/finalize", response_model=FinalizeResponse)
def finalize(intent_id: str, inp: FinalizeIn) -> FinalizeResponse:
    item = store.get(intent_id)
    if item is None:
        raise HTTPException(status_code=404, detail="not_found")
    if item.status != "DRAFT":
        raise HTTPException(status_code=409, detail=f"invalid_status:{item.status}")

    # Build execution request and ask Permit. BL-17 does not execute itself.
    exec_request = {
        "kind": "EXECUTION_REQUEST",
        "source": "BL17_INTENT_GATEWAY",
        "intent_id": item.intent_id,
        "requested_by": inp.approver_id,
        "requested_at_utc": utc_now(),
        "action_type": item.action_type,
        "target": item.target,
        "parameters": item.parameters,
        "channel": item.channel,
        "original_input": item.original_input,
    }

    permit_decision = permit.request_permit(exec_request).model_dump()

    if permit_decision.get("decision") != "ALLOW":
        # Fail-closed: do not publish operational request.
        item.status = "REJECTED"
        item.finalized_by = inp.approver_id
        item.finalized_at_utc = utc_now()
        item.final_approval_id = permit_decision.get("permit_id")
        item.trace_id = permit_decision.get("trace_id")
        store.upsert(item)
        return FinalizeResponse(intent=item, permit_decision=permit_decision, publish={"published": False, "mode": "fail_closed"})

    # Allowed: publish to Event Fabric (AACP)
    item.status = "FINALIZED"
    item.finalized_by = inp.approver_id
    item.finalized_at_utc = utc_now()
    item.final_approval_id = permit_decision.get("permit_id")
    item.trace_id = permit_decision.get("trace_id")
    store.upsert(item)

    publish_meta = publisher.publish_exec_request(exec_request)
    return FinalizeResponse(intent=item, permit_decision=permit_decision, publish=publish_meta)

# --- BL-13 thin proxy (for UI convenience) ---
@app.get("/v1/suggestions")
def list_suggestions(status: Optional[str] = Query(default=None)) -> Any:
    return reco.list_suggestions(status=status)

@app.get("/v1/suggestions/{suggestion_id}")
def get_suggestion(suggestion_id: str) -> Any:
    return reco.get_suggestion(suggestion_id)

@app.post("/v1/suggestions/{suggestion_id}/decision")
def decide_suggestion(suggestion_id: str, payload: Dict[str, Any]) -> Any:
    # payload example: { "reviewer_id": "...", "decision": "ACCEPT|REJECT|MODIFY", ... }
    return reco.decide(suggestion_id, payload)
