# ADR: Chain Hash Strategy (Phase 1)

Decision:
Chain hash is maintained per (topic, partition).

Rationale:
- Deterministic
- Minimal latency
- No cross-partition state

Rule:
Missing or invalid chain_hash => DENY
