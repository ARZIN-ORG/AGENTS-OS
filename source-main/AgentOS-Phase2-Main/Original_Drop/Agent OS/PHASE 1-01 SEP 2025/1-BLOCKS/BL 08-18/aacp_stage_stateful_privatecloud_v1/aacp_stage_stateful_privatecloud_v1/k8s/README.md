# K8s manifests (Private Cloud)

This folder contains minimal manifests for:
- PostgreSQL (StatefulSet + PVC)
- BL-13 v2 (Deployment)
- BL-17 v2 (Deployment)

Assumptions:
- You will replace images with your internal registry builds.
- Secrets must be replaced in your secret manager (sealed-secrets / external-secrets).
- NetworkPolicy should be tightened by DevOps per your cluster baseline.

Important:
- BL-13 uses strict audit mode by default: if Audit Sink is down, accept/decision path fails (governance-first).
