# Step 7 — Test Harness (Strict) + Chaos / Fail Cases (Phase-1)

This harness is designed for a **cynical CTO**.
Goal: prove the system fails closed, stays auditable, and rejects bypass attempts.

Scope (Phase-1):
- Interceptor/Manager wiring (Step 6)
- Audit Sink (Step 5)
- Registry/Policy/Permit/Trust stubs or real services (BL06/BL07/BL08/BL03)
- Kafka path optional (you can run against HTTP "guard" endpoints if Kafka isn't wired in your lab yet)

## What this harness tests
1) Envelope required-fields enforcement
2) Signature validation failures (tamper / wrong key / unknown key id)
3) Policy deny (topic/channel mismatch)
4) Permit deny (no human approval / missing permit id)
5) Audit down (publish path must reject / fail-closed)
6) Chain hash continuity (optional strict mode)
7) Replay / duplicate `event_id`
8) Time window violations (`expires_at_ms` / clock skew)
9) Channel rules: parallel channels allowed, but must be declared and enforced

## How to run
Prereqs: Python 3.11+

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python run_suite.py --config configs/lab_local.json
```

The suite outputs:
- machine-readable JSON report: `reports/latest.json`
- human summary: `reports/latest.txt`

## Configuration
See `configs/lab_local.json`.
Set endpoints for:
- audit sink
- signature verifier / trust service
- policy plane
- permit service
- registry (optional; used for extra checks)

## CTO note
This harness does **not** "assume happy path".
It assumes everyone is trying to bypass governance.

Generated: 2026-01-06 18:34:14 UTC
