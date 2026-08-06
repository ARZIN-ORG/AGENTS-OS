from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Policy Plane Service (OS-Native)", version="v1")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

@app.exception_handler(RejectError)
def reject_handler(_, exc: RejectError):
    return JSONResponse(status_code=400, content={"reject": True, "code": exc.code, "message": exc.message})

class PolicyResolveRequest(BaseModel):
    governance_output: Dict[str, Any]

@app.post("/resolve")
def resolve(req: PolicyResolveRequest, hdr=Depends(aacp_guard)):
    from agents.os_native.policy_plane import resolve as _resolve
    out = _resolve(req.governance_output)
    return {"hdr": hdr, "policy": out, "log": log_event("policy.resolve", {"trace_id": hdr["trace_id"]})}
