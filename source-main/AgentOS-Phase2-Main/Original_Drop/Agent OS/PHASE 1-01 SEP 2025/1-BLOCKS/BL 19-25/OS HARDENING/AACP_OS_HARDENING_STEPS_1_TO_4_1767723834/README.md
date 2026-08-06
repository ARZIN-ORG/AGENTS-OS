# AACP Agent OS (Phase 1) — Steps 1–4 Hardening Bundle

This bundle delivers **Step 1–4** of "OS hardening" in a CTO-grade, microservice-ready layout:

1) **Monorepo structure** (`services/`, `agents/`, `libs/`, `deploy/`)
2) **Fail-fast enforcement** for locked constraints (no bypass)
3) **AACP Gate hardening** via shared request validator (headers + audit envelope contract)
4) **Agents converted to deployable microservices** (FastAPI + health/readiness + OpenAPI docs)

## Locked Constraints (non-negotiable)
- Phase 1/2: **No agent makes final decisions**. Only recommendations.
- **Human-in-the-loop** is mandatory for any action. Permit is the gate.
- **Voice/Text never publishes operational messages directly.**
- Operational publish/consume must pass the **AACP path** (permit + audit + trace).
- Private Cloud deployment target.

## Services (OS-Native)
- Governance Service
- Policy Plane Service
- Permit Service
- Audit Sink Service
- Channel Manager Service
- Registry & Identity Service
- Signature & Trust Service

## Run (dev)
Each service is a FastAPI app. Example:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r services/policy_plane_service/requirements.txt
uvicorn services.policy_plane_service.app:app --reload --port 8011
```

## K8s (private cloud)
See `deploy/k8s/` for manifests (baseline).

Version: v1.0
Generated: 2026-01-06 18:23:54 UTC
