from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Registry & Identity Service (OS-Native)", version="v1")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

@app.exception_handler(RejectError)
def reject_handler(_, exc: RejectError):
    return JSONResponse(status_code=400, content={"reject": True, "code": exc.code, "message": exc.message})

class RegisterRequest(BaseModel):
    agent_id: str
    metadata: Dict[str, Any]

@app.post("/register")
def register(req: RegisterRequest, hdr=Depends(aacp_guard)):
    from agents.os_native.registry import register as _register
    out = _register(req.agent_id, req.metadata)
    return {"hdr": hdr, "result": out, "log": log_event("registry.register", {"trace_id": hdr["trace_id"], "agent_id": req.agent_id})}
