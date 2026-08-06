

- Apply `networkpolicy.yaml` after aligning labels.
- Run behind a gateway that verifies JWT and injects X-Auth-* headers.


- mTLS: apply `mtls-secret-example.yaml` (with real base64), then patch deploy via `bl19-deployment-mtls-patch.yaml`.
- Also apply `networkpolicy_permit_policy.yaml` to harden Permit/Policy planes.
