from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Permit Service (OS-Native)", version="v1")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

@app.exception_handler(RejectError)
def reject_handler(_, exc: RejectError):
    return JSONResponse(status_code=400, content={"reject": True, "code": exc.code, "message": exc.message})

class PermitRequest(BaseModel):
    policy: Dict[str, Any]
    human_approved: bool

@app.post("/issue")
def issue(req: PermitRequest, hdr=Depends(aacp_guard)):
    from agents.os_native.permit import issue as _issue
    out = _issue(req.policy, req.human_approved)
    return {"hdr": hdr, "permit": out, "log": log_event("permit.issue", {"trace_id": hdr["trace_id"]})}
