# BL-13 — Recommendation Plane (Phase 1) — v2 (Stateful + Audit Emit)

Delta vs v1:
- Replaces in-memory store with SQLAlchemy persistence.
- Emits audit records to BL-08 Audit Sink for key lifecycle events:
  SUGGESTION_CREATED / SUGGESTION_REVIEWED / SUGGESTION_ACCEPTED / SUGGESTION_REJECTED.

Locked rules remain enforced:
- Suggestions are non-executable artifacts.
- Execution only after human acceptance and only via Permit (+ Audit + Trace).
- Fail-closed on Permit errors.
- No UI/Voice/Text channel can directly publish operational messages.

Environment:
- DATABASE_URL: e.g. postgresql+psycopg2://user:pass@host:5432/bl13
- AACP_PERMIT_URL: http://permit-service:8080
- AACP_AUDIT_SINK_URL: http://audit-sink:8080
- AACP_EXEC_REQUEST_TOPIC: aacp.exec.request
