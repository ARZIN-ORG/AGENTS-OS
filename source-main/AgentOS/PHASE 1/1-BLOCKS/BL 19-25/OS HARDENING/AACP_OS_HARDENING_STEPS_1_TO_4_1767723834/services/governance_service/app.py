from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Governance Service (OS-Native)", version="v1")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

@app.exception_handler(RejectError)
def reject_handler(_, exc: RejectError):
    return JSONResponse(status_code=400, content={"reject": True, "code": exc.code, "message": exc.message})

class GovernanceRequest(BaseModel):
    context: Dict[str, Any]

@app.post("/evaluate")
def evaluate(req: GovernanceRequest, hdr=Depends(aacp_guard)):
    from agents.os_native.governance import evaluate as _eval
    out = _eval(req.context)
    return {"hdr": hdr, "result": out, "log": log_event("governance.evaluate", {"trace_id": hdr["trace_id"]})}
