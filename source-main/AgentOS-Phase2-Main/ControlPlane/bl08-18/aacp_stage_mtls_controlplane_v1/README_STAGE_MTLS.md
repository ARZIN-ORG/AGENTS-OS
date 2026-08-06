# Stage — Control Plane mTLS (Phase-1 Hardening)

What this delivers:
- Intent Gateway -> Permit Service over HTTPS with mTLS (client cert auth).
- Permit Service -> Policy Plane over HTTPS with mTLS.
- Permit Service -> Audit Sink over HTTPS with mTLS (if enabled).
- NetworkPolicies to restrict traffic paths.

Important:
- This bundle provides client-side mTLS wiring in code and k8s patches.
- You must configure servers (Permit/Policy/Audit) to expose an mTLS port (e.g., 8443).
  Best enforced by a gateway/service mesh in Private Cloud (DevOps-owned).

Files:
- k8s/mtls-secrets-example.yaml
- k8s/intent-gateway-mtls-patch.yaml
- k8s/permit-service-mtls-patch.yaml
- k8s/networkpolicy_intent_permit_policy.yaml
