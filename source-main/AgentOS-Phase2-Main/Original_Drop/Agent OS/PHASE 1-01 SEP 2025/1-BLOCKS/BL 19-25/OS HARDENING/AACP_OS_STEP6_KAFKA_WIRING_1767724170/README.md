# Step 6 — Kafka Interceptor Wiring (Fail-Closed AACP Gate)

This bundle provides a **strict Kafka interceptor + wiring** that enforces the Phase-1 locks:
- No direct operational publish without **Signature Verify -> Policy Resolve -> Permit Check -> Audit Append**
- **Fail-closed** on any missing/invalid requirement
- Works as a **library** embedded in producer/consumer apps (or SOHA hook layer)

## What it does (producer path)
1) Validate required AACP headers (contract)
2) Verify signature with `signature_trust_service`
3) Resolve policy with `policy_plane_service`
4) Check/issue permit with `permit_service` (must reflect human approval upstream)
5) Append audit record with `audit_sink_service` (chain hash supported)
6) Publish to Kafka only if all checks pass

## What it does (consumer path)
1) Validate headers
2) Verify signature
3) Append audit "consume" record
4) Hand payload to the consumer handler

## Services expected (HTTP endpoints)
- Signature & Trust: `POST /verify`
- Policy Plane: `POST /resolve`
- Permit: `POST /issue` or `POST /check` (this bundle uses `/issue` with `human_approved` flag)
- Audit Sink: `POST /append`

## Env vars
- AACP_TRUST_URL (default http://signature_trust_service:8000)
- AACP_POLICY_URL (default http://policy_plane_service:8000)
- AACP_PERMIT_URL (default http://permit_service:8000)
- AACP_AUDIT_URL (default http://audit_sink_service:8000)
- AACP_KAFKA_BOOTSTRAP (default localhost:9092)
- AACP_CHANNEL_ID (default channel::default)

## Notes
- This is **CTO-grade wiring**, not a demo. It rejects aggressively.
- It does not “decide”. It enforces the **permit gate**.
- Voice/Text never publishes operational messages directly (must go via Intent->Human approval->Permit).

Generated: 2026-01-06 18:29:30 UTC
