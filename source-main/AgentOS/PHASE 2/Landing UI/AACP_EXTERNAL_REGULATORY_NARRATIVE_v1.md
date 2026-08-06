# AACP Agent OS — External Regulatory Narrative (Phase‑1)
Version: v1.0
Date: 2026-01-07
Audience: Regulator / Auditor / Strategic Partner

## 1) What this is
AACP (AI‑Agent Communication Protocol) is the operational trust layer for Agent OS.
It standardizes how system components exchange events, how actions are authorized, and how every step becomes reconstructable evidence.

This document describes how the platform stays governable in Phase‑1:
Agents generate Recommendations; humans approve; the system executes only under Permit and always produces an auditable trace.

## 2) What this is not
AACP is not an autonomous decision-maker.
AACP is not a marketing “AI platform.”
AACP does not bypass human accountability.

## 3) Governance principle (Phase‑1 locked)
No agent can execute decisions directly.
All actions follow a mandatory chain:
Identity (MFA) → Capture (Voice/Text) → Intent translation → Human review/edit → Human approval → Permit issuance → Execution via AACP → Immutable audit → Management reporting.

If any link is missing, execution is rejected (fail-fast).

## 4) Control Plane vs Data Plane
Control Plane enforces governance:
- Agent Registry (identity, versions, ownership, allowed domains)
- Policy Plane (versioned policies, constraints, red lines)
- Permit Service (explicit authorization for each action)
- Channel Manager (which channels/topics are allowed)
- Audit & Trace (immutable evidence, chain hash)

Data Plane transports events:
- AACP messages over event fabric (e.g., Kafka) using standard schemas and envelope fields.
- Interceptors validate every message before it is accepted.

This separation prevents “innovation chaos” and keeps growth investable.

## 5) Traceability and evidence
Each AACP event carries an Audit Envelope that includes:
unique IDs, timestamps, actor identity, policy version, permit reference, channel/topic, payload hash, signature metadata, and chain hash pointers.

Result:
- We can reconstruct “how” and “why,” not just “what happened.”
- Audit does not depend on the internal implementation of any single agent.
- Replacing an agent does not erase accountability.

## 6) Security model (overview)
- Strong identity for humans and services (MFA for management, mTLS for service-to-service where required).
- Role separation: Policy Author ≠ Developer; Operator ≠ Auditor; Governance ≠ Execution.
- End‑to‑end message integrity: signatures verified at the edge via keystore/HSM-backed trust.
- Channel authorization: agents can publish/consume only on approved channels.

## 7) Human dignity and contestability
The system is designed to keep humans in control:
- Every suggestion is shown before approval.
- Managers can edit, reject, or request clarification.
- The system stores the rationale and evidence that led to the recommendation.
This supports contestability and review.

## 8) Operational resilience
The platform is designed to fail safe:
- Missing Permit → reject + DLQ + audit record.
- Invalid signature → reject + security event + audit record.
- Policy mismatch → block or require re-resolution.
- Audit sink issues → no “successful execution” without durable audit evidence.

## 9) What external partners must do
External partners integrate via:
- Published AACP spec + SDK skeleton
- Mandatory envelope fields
- Required signature and identity model
- Permit workflow compliance
- Audit trace compatibility

Integration is assessed through a controlled sandbox and a shadow pilot before production exposure.

## 10) Assurance statement
AACP does not promise trust; it produces evidence.
The architecture is built to preserve accountability, reconstructability, and controlled evolution under governance.

## 11) Appendices (available on request)
- AACP Public Spec (Phase‑1)
- Partner Onboarding Framework
- GameDay evidence pack template
- KPIs/KRIs for continuous compliance
