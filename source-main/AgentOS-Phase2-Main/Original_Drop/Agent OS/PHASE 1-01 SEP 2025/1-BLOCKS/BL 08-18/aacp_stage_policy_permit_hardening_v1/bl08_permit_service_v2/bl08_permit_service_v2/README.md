# BL-08 — Permit Service (Phase 1) — v2 (Policy-aware + Channel/Scope/Action enforcement)

Purpose:
- Central "Permit" decision point for any EXECUTION_REQUEST in Phase-1.
- Hard fail-closed by design.

What this adds:
- Policy Plane lookup (BL-07) per (actor_id, action_type, channel, scope).
- Deny-by-default if policy missing or policy-plane unavailable.
- Replay protection (permit_id deterministic per request hash if configured).
- Minimal rate-limit for permit endpoint (defense-in-depth).

Environment:
- POLICY_PLANE_URL: http://policy-plane:8080
- PERMIT_MAX_SKEW_SECONDS: default 120
- PERMIT_REQUIRE_REQUEST_ID: true/false (default true)
- PERMIT_RATE_LIMIT_PER_MINUTE: default 1200

Request fields expected (subset, enforced):
- kind == EXECUTION_REQUEST
- requested_by
- requested_at_utc (ISO8601)
- action_type
- channel (VOICE/TEXT/CONTROL)
- request_id (uuid-like)  [required if PERMIT_REQUIRE_REQUEST_ID=true]
- scope (string)          [optional but recommended]
