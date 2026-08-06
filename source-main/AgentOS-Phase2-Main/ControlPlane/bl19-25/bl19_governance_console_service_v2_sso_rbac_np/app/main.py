# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel

from .schemas import HealthOut, TimelineOut, KPIOut, ChainVerifyOut, AuditEvent
from .auth import OidcJwtValidator
from .clients import AuditSinkClient
from .chain import verify_chain

APP_NAME = "BL-19 Governance Console (Read-Only)"
app = FastAPI(title=APP_NAME, version="0.1.0")

DEFAULT_WINDOW = int(os.getenv("DEFAULT_WINDOW_HOURS", "24"))
TIMEOUT = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "4.0"))

audit = AuditSinkClient(timeout_s=TIMEOUT)
authz = OidcJwtValidator()

@app.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    upstream: Dict[str, Any] = {}
    ok = True
    try:
        upstream["audit_sink"] = audit.health()
    except Exception as e:
        upstream["audit_sink"] = {"ok": False, "error": str(e)}
        ok = False
    return HealthOut(ok=ok, service=APP_NAME, upstream=upstream)

@app.get("/v1/timeline", response_model=TimelineOut)
def timeline(
    request: Request,
    window_hours: int = Query(DEFAULT_WINDOW, ge=1, le=168),
    limit: int = Query(200, ge=1, le=5000),
    actor_id: Optional[str] = None,
    action_type: Optional[str] = None,
    channel: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> TimelineOut:
    authz.require_roles(request)

    try:
        raw = audit.fetch_events(window_hours=window_hours, limit=limit,
                                actor_id=actor_id, action_type=action_type,
                                channel=channel, trace_id=trace_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"audit_sink_unavailable: {e}")

    events = [AuditEvent(**r) for r in raw]
    return TimelineOut(window_hours=window_hours, count=len(events), events=events)

@app.get("/v1/kpi", response_model=KPIOut)
def kpi(request: Request, window_hours: int = Query(DEFAULT_WINDOW, ge=1, le=168)) -> KPIOut:
    authz.require_roles(request)

    authz.require_roles(request)

    authz.require_roles(request)

    try:
        raw = audit.fetch_events(window_hours=window_hours, limit=5000)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"audit_sink_unavailable: {e}")

    total = len(raw)
    allow = 0
    deny = 0
    by_channel: Dict[str, int] = {}
    by_action: Dict[str, int] = {}

    for e in raw:
        d = (e.get("decision") or "").upper()
        if d == "ALLOW":
            allow += 1
        elif d == "DENY":
            deny += 1
        ch = (e.get("channel") or "UNKNOWN").upper()
        by_channel[ch] = by_channel.get(ch, 0) + 1
        act = e.get("action_type") or "UNKNOWN"
        by_action[act] = by_action.get(act, 0) + 1

    return KPIOut(
        window_hours=window_hours,
        total=total,
        allow=allow,
        deny=deny,
        by_channel=by_channel,
        by_action=by_action,
    )

@app.get("/v1/chain/verify", response_model=ChainVerifyOut)
def chain_verify(request: Request, window_hours: int = Query(DEFAULT_WINDOW, ge=1, le=168)) -> ChainVerifyOut:
    authz.require_roles(request)

    authz.require_roles(request)

    try:
        raw = audit.fetch_events(window_hours=window_hours, limit=5000)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"audit_sink_unavailable: {e}")

    ok, idx, reason = verify_chain(raw)
    return ChainVerifyOut(window_hours=window_hours, checked=len(raw), ok=ok, broken_at_index=idx, reason=reason)
