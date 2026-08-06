# BL-19 — Governance Console (Read-Only) — Phase 1

This service is **read-only** by design.
It provides management/regulator-friendly visibility over the AACP decision chain without any ability to publish/execute.

Core guarantees (Phase-1 lock):
- No endpoint performs publish to AACP topics.
- No endpoint calls execution services.
- Only pulls from Audit Sink / Permit / Policy as configured.
- If upstream audit is unavailable, console reports degraded state (no silent masking).

## What you get
- Timeline of decisions/events (from Audit Sink).
- Chain integrity checks (best-effort: local re-hash verification on returned records).
- KPI/KRI snapshots (counts of ALLOW/DENY, by action/channel, last N hours).
- Search/filter by actor_id, action_type, channel, trace_id, time range.

## Configuration
- AUDIT_SINK_URL (default: http://audit-sink:8080)
- PERMIT_URL (optional) (default: http://permit-service:8080)
- POLICY_PLANE_URL (optional) (default: http://policy-plane:8080)
- DEFAULT_WINDOW_HOURS (default: 24)
- REQUEST_TIMEOUT_SECONDS (default: 4.0)

## Run (local)
pip install -e .
uvicorn app.main:app --host 0.0.0.0 --port 8080

## Notes
This is intentionally minimal for Phase-1.
In Phase-2 you can add SSO, RBAC, UI, export packs, regulator views, etc.
