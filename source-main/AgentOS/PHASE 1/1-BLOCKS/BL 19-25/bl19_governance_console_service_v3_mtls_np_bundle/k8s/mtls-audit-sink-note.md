# Audit Sink mTLS (Phase-1 hardening note)

This package provides mTLS on the client side (BL-19 -> Audit Sink).
You must configure Audit Sink to serve HTTPS with client cert auth (mTLS) on a dedicated port (e.g., 8443).

Operational rules:
- Use an internal CA for cluster services.
- Rotate client certs on a schedule.
- Console must fail-closed if TLS verification fails.

This is intentionally handled by DevOps via Ingress/Gateway or service mesh (preferred).
