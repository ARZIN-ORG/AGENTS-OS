# BL-17 — Omni-Channel Intent Gateway (Phase 1) — v2 (Stateful)

Delta vs v1:
- Persists intent drafts and finalizations in SQL database (PostgreSQL recommended).

Locked flow preserved:
MFA -> Receive Voice/Text -> Translate to Intent Draft -> Show to human -> Edit/Reject -> Final human approval -> Permit -> Publish via AACP -> Management report.

Environment:
- DATABASE_URL: e.g. postgresql+psycopg2://user:pass@host:5432/bl17
- AACP_PERMIT_URL: http://permit-service:8080
- BL13_RECOMMENDATION_URL: http://recommendation-plane:8080
- AACP_EXEC_REQUEST_TOPIC: aacp.exec.request
