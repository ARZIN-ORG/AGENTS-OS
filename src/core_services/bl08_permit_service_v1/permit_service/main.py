from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="ARZIN Permit Service", version="1.0")

class Envelope(BaseModel):
    trace_id: str
    ttl_seconds: int
    payload_bytes: int
    signature_valid: bool

class PermitRequest(BaseModel):
    agent_id: str
    agent_class: str
    channel_id: str
    topic: str
    envelope: Envelope

class PermitDecision(BaseModel):
    decision: str
    reason: str
    policy_id: str | None = None
    policy_version: int | None = None
    trace_id: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/permit", response_model=PermitDecision)
def permit(req: PermitRequest):
    # Phase 1 hard rules
    if not req.envelope.signature_valid:
        return PermitDecision(
            decision="DENY",
            reason="invalid_signature",
            trace_id=req.envelope.trace_id
        )
    if req.envelope.ttl_seconds <= 0:
        return PermitDecision(
            decision="DENY",
            reason="ttl_expired",
            trace_id=req.envelope.trace_id
        )
    # Placeholder: real lookup via BL-06 & BL-07 happens via HTTP/gRPC
    return PermitDecision(
        decision="ALLOW",
        reason="phase1_allow",
        policy_id="default",
        policy_version=1,
        trace_id=req.envelope.trace_id
    )
