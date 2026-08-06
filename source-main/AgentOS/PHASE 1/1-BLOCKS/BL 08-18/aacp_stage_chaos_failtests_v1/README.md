# AACP Phase-1 — Chaos / Fail-Closed Test Pack (v1)

Purpose:
- Prove the system **fails closed** under broken dependencies and invalid inputs.
- Generate repeatable evidence for a strict CTO and auditors.

What’s included:
1) Kubernetes manifests for controlled failures:
   - scale down Audit Sink
   - block egress from Permit to Policy (NetworkPolicy toggle)
   - simulate Kafka broker outage (label-based deny policy)
2) Python test runner that executes negative cases:
   - missing/invalid signatures -> reject + DLQ
   - missing permit -> deny
   - audit unreachable -> deny or explicit failure (no silent success)
   - policy unreachable -> deny
   - chain hash mismatch -> reject

Requirements:
- `kubectl` configured for the cluster/namespace
- AACP services deployed in namespace `aacp` (adjust if different)
- Python 3.10+ for the runner

All tests must be non-destructive beyond temporary scaling/networkpolicy toggles.
