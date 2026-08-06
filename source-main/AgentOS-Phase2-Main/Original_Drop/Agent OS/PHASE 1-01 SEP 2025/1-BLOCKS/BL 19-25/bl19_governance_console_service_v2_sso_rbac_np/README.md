# BL-19 — Governance Console (Read-Only) — Phase 1 — v2 (SSO/RBAC + NetworkPolicy)

This service remains **read-only** by design.
It adds **SSO-ready auth** (OIDC JWT validation) and **app-level RBAC** gates, plus K8s NetworkPolicy templates.

Non-negotiables (Phase-1 lock):
- No endpoint publishes to AACP topics.
- No endpoint triggers execution.
- Fail-closed on auth: invalid/missing token => 401/403.
- Degraded upstream (Audit Sink down) is explicit (502).

## Auth / SSO (OIDC)
We validate Bearer JWTs using a JWKS endpoint (Keycloak/Okta/Auth0/etc.).

Env:
- OIDC_JWKS_URL (required for auth enforcement)
- OIDC_ISSUER (optional but recommended)
- OIDC_AUDIENCE (optional but recommended)
- OIDC_ROLE_CLAIM (default: realm_access.roles)
- OIDC_ALLOWED_ROLES (comma list; default: aacp-admin,aacp-auditor,aacp-ops)

Auth modes:
- STRICT (default): token required on every /v1/* endpoint.
- OFF (dev only): set AUTH_MODE=off

## RBAC
All endpoints are read-only but still gated:
- timeline/kpi/chain endpoints require at least one allowed role.

## NetworkPolicy (Private Cloud)
`k8s/networkpolicy.yaml` includes:
- Ingress only from namespaces/pods labeled for management access.
- Egress only to Audit Sink service (and DNS).

You MUST align labels with your cluster standards (DevOps-owned).

## Run
pip install -e .
export OIDC_JWKS_URL="https://<idp>/realms/<realm>/protocol/openid-connect/certs"
uvicorn app.main:app --host 0.0.0.0 --port 8080
