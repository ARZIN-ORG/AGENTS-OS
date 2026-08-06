# Step 5 — Audit Sink (Stateful) + Chain Hash (Phase-1)

This service is the **immutable-ish** audit sink for AACP Phase-1.
It provides:
- `POST /append` : append an audit record and return `chain_hash`
- `GET /healthz` and `GET /readyz`
- `GET /records` : query recent records (admin/debug)
- `GET /records/{id}` : fetch record by id

## Storage
Default: SQLite on a mounted volume (`/var/lib/aacp/audit.db`) — suitable for Phase-1 private cloud pilot.
Optional: Postgres (via `AACP_AUDIT_DB_URL`) if you want HA sooner.

## Chain hash
`chain_hash = SHA256(prev_chain_hash + canonical_json(envelope) + payload_digest + seq)`
- `prev_chain_hash` is accepted from client; service verifies continuity if `AACP_AUDIT_ENFORCE_CHAIN=true`.
- Service also stores `prev_chain_hash` and `chain_hash` per record.
- Interceptor must treat missing chain_hash as **reject** (already done in Step 6).

## Retention
- Soft retention by days: `AACP_AUDIT_RETENTION_DAYS` (default 365)
- Cleanup job runs opportunistically on append if enabled (`AACP_AUDIT_ENABLE_RETENTION=true`).

## Why "stateful" matters
If Audit is down/slow, the operational publish path must **fail-closed**.
This service is therefore a first-class component, not "logging".

Generated: 2026-01-06 18:31:36 UTC
