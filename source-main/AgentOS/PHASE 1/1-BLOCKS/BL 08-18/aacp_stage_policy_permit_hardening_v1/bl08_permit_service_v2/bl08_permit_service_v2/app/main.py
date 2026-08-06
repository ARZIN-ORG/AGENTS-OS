# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import hashlib

from fastapi import FastAPI, HTTPException, Request
from pydantic import ValidationError

from .schemas import ExecutionRequest, PermitDecision
from .policy_client import PolicyClient
from .replay import InMemoryReplayGuard
from .ratelimit import SimpleRateLimiter

APP_NAME = "BL-08 Permit Service (Phase 1) v2"
app = FastAPI(title=APP_NAME, version="0.2.0")

policy = PolicyClient()
replay = InMemoryReplayGuard(ttl_s=int(os.getenv("PERMIT_REPLAY_TTL_SECONDS", "600")))
rl = SimpleRateLimiter(per_minute=int(os.getenv("PERMIT_RATE_LIMIT_PER_MINUTE", "1200")))

MAX_SKEW = int(os.getenv("PERMIT_MAX_SKEW_SECONDS", "120"))
REQUIRE_REQUEST_ID = os.getenv("PERMIT_REQUIRE_REQUEST_ID", "true").lower() in ("1","true","yes")

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

def _parse_iso(s: str) -> datetime:
    # strict-ish: must be ISO8601 with timezone
    return datetime.fromisoformat(s.replace("Z", "+00:00"))

def _permit_id(fp: str) -> str:
    return f"permit_{fp[:16]}"

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "service": APP_NAME}

@app.post("/v1/permit", response_model=PermitDecision)
async def permit_endpoint(req: Request) -> PermitDecision:
    # coarse rate limit per client ip (gateway should do more)
    ip = req.client.host if req.client else "unknown"
    if not rl.allow(ip):
        return PermitDecision(permit_id="n/a", decision="DENY", reason="rate_limited", trace_id=None)

    raw = await req.json()
    try:
        er = ExecutionRequest(**raw)
    except ValidationError:
        return PermitDecision(permit_id="n/a", decision="DENY", reason="invalid_request_schema", trace_id=None)

    if REQUIRE_REQUEST_ID and not er.request_id:
        return PermitDecision(permit_id="n/a", decision="DENY", reason="missing_request_id", trace_id=None)

    # time skew check
    try:
        t = _parse_iso(er.requested_at_utc)
    except Exception:
        return PermitDecision(permit_id="n/a", decision="DENY", reason="bad_requested_at_utc", trace_id=None)

    skew = abs((_utc_now() - t).total_seconds())
    if skew > MAX_SKEW:
        return PermitDecision(permit_id="n/a", decision="DENY", reason="clock_skew", trace_id=None)

    # replay guard
    fp = replay.fingerprint(raw)
    ok, reason = replay.check_and_mark(fp)
    if not ok:
        return PermitDecision(permit_id=_permit_id(fp), decision="DENY", reason=reason, trace_id=None)

    # policy lookup (deny-by-default on any error)
    try:
        pol = policy.resolve(er.requested_by, er.action_type, er.channel, er.scope)
    except Exception:
        return PermitDecision(permit_id=_permit_id(fp), decision="DENY", reason="policy_unavailable", trace_id=None)

    # expected policy response:
    # { "allow": true/false, "policy_id": "...", "policy_version": "...", "reason": "..." }
    allow = bool(pol.get("allow", False))
    if not allow:
        return PermitDecision(permit_id=_permit_id(fp), decision="DENY", reason=pol.get("reason","policy_deny"), trace_id=None)

    trace_id = pol.get("trace_id") or hashlib.sha256(fp.encode("utf-8")).hexdigest()[:24]
    return PermitDecision(permit_id=_permit_id(fp), decision="ALLOW", reason=None, trace_id=trace_id)
