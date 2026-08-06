# AACP Phase-1 — Certificate Rotation Automation (v1)

This bundle provides **DevOps-owned** automation primitives for rotating internal mTLS certificates.
It is intentionally conservative and **does not** attempt to be a full PKI product.

Assumptions:
- You have an internal CA (or intermediate) used for cluster-service mTLS.
- Services consume certs via Kubernetes Secrets mounted as files.
- Restart/rollout is acceptable per service after secret update.

What’s included:
- A Kubernetes CronJob that runs a rotation script on a schedule.
- A rotation script that:
  1) requests/creates new certs (stubbed interface),
  2) updates Kubernetes Secrets,
  3) triggers rolling restart for target deployments/statefulsets,
  4) writes an audit record to stdout (to be collected by cluster logging).

Important:
- The script contains a **PKI provider interface**. You must implement one of:
  - Vault PKI
  - cert-manager (preferred)
  - your existing CA automation
- Fail-closed policy: if rotation fails, it must not partially update secrets.
