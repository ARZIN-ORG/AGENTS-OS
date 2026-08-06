# Kafka mTLS Hardening — AACP Phase-1

Goals:
- Encrypt broker/client traffic
- Enforce mutual auth with certificates
- Restrict publish/consume via ACLs

Steps:
1. Generate internal CA.
2. Issue broker cert and client certs (one per service).
3. Create keystore/truststore JKS files.
4. Apply k8s secrets and deployment patch.
5. Apply ACLs for topics/groups.
6. Disable PLAINTEXT listener.

Rules:
- One cert per service identity.
- Rotate certs periodically.
- No wildcard ACLs in prod.
