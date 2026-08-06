# ADR-0005: Audit Sink as Stateful Service + Chain Hash (Phase-1)

## Context
AACP Phase-1 requires immutable-ish audit trails and strict accountability. Audit is not optional logging; it is part of the protocol enforcement chain.

## Decision
Introduce `audit_sink_service` as a Stateful component with persisted storage (PVC) and a chain hash returned for each append. Producer/Consumer publish paths must fail-closed if audit append fails or chain hash is missing.

## Rationale
- Enables end-to-end traceability with tamper-evidence (chain hash).
- Decouples audit capability from agent implementation internals.
- Provides a regulator-grade narrative: “we produce evidence, not promises”.

## Consequences
- Audit becomes a critical dependency; availability must be engineered (Phase-2 may move to Postgres/HA backend).
- Throughput must be validated; batching can be introduced later but cannot bypass audit requirements.
