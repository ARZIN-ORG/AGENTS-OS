from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Audit Sink Service (OS-Native)", version="v1")

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/readyz")
def readyz():
    return {"ready": True}

@app.exception_handler(RejectError)
def reject_handler(_, exc: RejectError):
    return JSONResponse(status_code=400, content={"reject": True, "code": exc.code, "message": exc.message})

import os
from libs.aacp_common.audit import AuditEnvelope
from libs.aacp_common.audit import require_fields

AUDIT_FILE = os.getenv("AACP_AUDIT_FILE", "/tmp/aacp_audit.log")

class AuditAppendRequest(BaseModel):
    envelope: Dict[str, Any]
    payload_digest: Optional[str] = None
    prev_chain_hash: Optional[str] = None

@app.post("/append")
def append(req: AuditAppendRequest, hdr=Depends(aacp_guard)):
    missing = require_fields(req.envelope)
    if missing:
        raise RejectError("AUDIT_ENVELOPE_MISSING_FIELDS", f"Missing audit envelope fields: {missing}")

    env = AuditEnvelope(**req.envelope)
    chain_hash = env.compute_chain_hash(req.prev_chain_hash)
    rec = {
        "hdr": hdr,
        "envelope": env.model_dump(),
        "payload_digest": req.payload_digest,
        "prev_chain_hash": req.prev_chain_hash,
        "chain_hash": chain_hash,
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(log_event("audit.append", rec) + "\n")

    return {"ok": True, "chain_hash": chain_hash}
