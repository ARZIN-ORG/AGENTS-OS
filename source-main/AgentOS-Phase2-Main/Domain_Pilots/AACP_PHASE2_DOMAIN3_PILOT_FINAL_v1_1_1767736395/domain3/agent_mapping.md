
# Agent Mapping to Agent OS (4 Layers)

## OS-Native (Control Plane)
- Audit & Trace Agent: source of truth for traces/evidence pointers
- Policy Plane Agent: provides policy context & versions
- Permit/Authorization Agent: provides human-approved decision checkpoints
- Registry & Identity Agent: identifies actor/service ownership
- Signature & Trust Agent: verifies integrity and provenance
- Channel Manager Agent: provides channel metadata/segmentation
- Governance Agent: controls visibility & publication rules

## Infrastructure
- Observability/Health inputs: Kafka/K8s metrics (read-only)

## Domain (This Pilot)
- Executive Insight Agent (Domain-3 core): generates insight cards with evidence links

## Interaction
- Executive Narrative Agent: formats and explains; never decides
