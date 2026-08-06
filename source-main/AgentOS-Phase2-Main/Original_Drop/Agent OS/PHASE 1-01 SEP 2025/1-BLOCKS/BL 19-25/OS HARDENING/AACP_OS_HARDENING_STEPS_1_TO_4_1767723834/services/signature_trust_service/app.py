from __future__ import annotations

from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, Optional
from libs.aacp_common.request_guard import aacp_guard
from libs.aacp_common.errors import RejectError
from libs.aacp_common.logging import log_event

app = FastAPI(title="Signature & Trust Service (OS-Native)", version="v1")

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
from libs.aacp_common.security import FileKeyStore, verify_hmac_sha256

KEY_ID = os.getenv("AACP_KEY_ID", "dev-key")
SECRET = os.getenv("AACP_DEV_SECRET", "change-me").encode("utf-8")
KS = FileKeyStore(SECRET)

class VerifyRequest(BaseModel):
    message: Dict[str, Any]
    signature_hex: str

@app.post("/verify")
def verify(req: VerifyRequest, hdr=Depends(aacp_guard)):
    # deterministic canonicalization
    import json
    blob = json.dumps(req.message, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ok = verify_hmac_sha256(KS, KEY_ID, blob, req.signature_hex)
    return {"hdr": hdr, "verified": ok, "log": log_event("trust.verify", {"trace_id": hdr["trace_id"], "ok": ok})}
