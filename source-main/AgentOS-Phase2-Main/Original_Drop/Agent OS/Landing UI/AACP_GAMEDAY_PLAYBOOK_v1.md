# AACP Agent OS — GameDay Playbook (Phase‑1, Human‑in‑the‑Loop Locked)
Version: v1.0
Date: 2026-01-07
Owner: Platform/Agent OS (CTO-level)

## 1) Purpose
This GameDay proves (not claims) that Phase‑1 Agent OS obeys the locked constraints:
- No agent makes final decisions in Phase‑1/2. Agents only generate Recommendations.
- Voice/Text inputs never publish operational messages directly.
- Every action path is: Identify (MFA) → Capture → Intent → Show to Human → Human edit/approve → Permit → Publish via AACP → Audit/Trace → Management report.
- Multi‑channel AACP is enforced; bypass routes fail fast.

Success means the system fails safe under stress, preserves traceability, and remains explainable to executives and auditors.

## 2) Scope
In scope:
- Governance Console UI (wired real mode) + BFF
- BL‑06 Registry, BL‑07 Policy Plane, BL‑08 Permit + Audit Sink, BL‑17 Intent Gateway, BL‑19 Governance Console service
- AACP Kafka interceptor/manager (Phase‑1 wired)
- Audit Envelope + chain hash
Out of scope (Phase‑2+ only):
- Auto‑execution, autonomous agents, marketplace onboarding at scale

## 3) Roles and Responsibilities
- Incident Commander (IC): runs the GameDay, owns timeline.
- CTO/Ops Lead: approves disruptive actions.
- Security Lead: verifies authz boundaries and tamper evidence.
- Auditor Role: reads traces and confirms “reconstructability.”
- Scribe: captures decisions, timestamps, and outcomes.

## 4) Preconditions (Hard Requirements)
1. Private Cloud environment deployed (K8s + Kafka) with mTLS where specified.
2. SSO/MFA enabled for management identities; RBAC roles present: Viewer/Reviewer/Approver/Auditor/Operator.
3. All services export health endpoints + metrics.
4. Audit sink is stateful and immutable (append-only) with chain hash enabled.
5. Feature flags: REAL_MODE only; Mock paths disabled for the test.

## 5) Evidence Pack (What must be produced)
For each scenario, produce:
- Trace ID(s)
- Permit ID(s)
- Policy version ID used
- Actor identity (human) and MFA proof reference
- Audit Envelope (10–15 required fields)
- Chain hash head/tail for the sequence
- Executive narrative (human-readable) generated and stored
- Postmortem note: expected vs observed

## 6) Scenario Matrix (Phase‑1 Critical)
### S1 — Happy Path: Text Intent → Approved → Published → Audited
Steps:
1) Manager enters text request in UI.
2) Intent Gateway produces structured intent; shows preview to manager.
3) Manager edits + approves.
4) Permit requested; Approver grants.
5) Publish via AACP channel; interceptor validates envelope/signature/policy/permit.
6) Audit sink persists with chain hash; narrative generated.

Pass criteria:
- No publish without Permit.
- Trace reconstructs full chain in < 2 minutes.
- Narrative matches Trace ID and Permit ID.

### S2 — Voice Path: Voice → Intent Preview → Human Approval
Steps:
1) MFA manager login.
2) Voice captured, transcribed.
3) Intent preview shown; manager edits.
4) Same path as S1.

Pass criteria:
- Voice never publishes.
- Human approval is logged as the decision point.
- Any STT error is visible before approval (no silent action).

### S3 — Missing Permit (Hard Fail)
Steps:
1) Attempt publish without Permit (simulate misbehaving producer).
Pass criteria:
- Interceptor rejects.
- Message routed to DLQ with reason code.
- Audit records rejection with traceable evidence.

### S4 — Policy Drift Detection (Stale Policy)
Steps:
1) Producer uses outdated policy version.
Pass criteria:
- Policy resolver detects mismatch.
- Publish blocked or forced to re-resolve.
- Audit captures “policy_mismatch” with version info.

### S5 — Signature Verification Failure
Steps:
1) Send message with invalid signature / wrong key id.
Pass criteria:
- Reject + DLQ.
- Security event emitted.
- No partial processing downstream.

### S6 — Channel Violation (Wrong Channel / Topic)
Steps:
1) Publish to unauthorized topic/channel.
Pass criteria:
- Channel manager denies.
- Audit shows denied by channel rule.
- No leakage into consumer topics.

### S7 — Kafka Partition / Broker Degradation
Steps:
1) Induce broker latency or partition loss (controlled).
Pass criteria:
- Backpressure visible.
- System stays consistent; no silent drops.
- Recovery path documented.

### S8 — Audit Sink Partial Outage
Steps:
1) Make audit sink unavailable.
Pass criteria:
- Publish is blocked OR buffered per locked rule (choose one and enforce).
- No “success” without audit durability.
- Clear operator alert.

### S9 — Registry Poisoning Attempt
Steps:
1) Attempt registering agent with duplicate identity or invalid attestation.
Pass criteria:
- Registry rejects.
- Audit records attempt with actor and reason.

### S10 — Replay Attack Simulation
Steps:
1) Re-send same message ID.
Pass criteria:
- Dedup triggers; no re-processing.
- Audit notes replay attempt.

## 7) SLO/Readiness Gates (Phase‑1)
- Trace retrieval p95 < 3s for last 24h (target)
- Rejection-to-DLQ p95 < 2s
- Permit decision logging 100%
- No bypass paths detected in routing graph

## 8) Runbook: Start/Stop and Safety
- Start with read-only consumers.
- Only IC can authorize fault injection.
- Any unexpected publish halts the GameDay (freeze permit issuance).
- Post-GameDay: export evidence pack to immutable storage.

## 9) Deliverables
- GameDay report (timeline + outcomes)
- List of defects with severity (P0/P1/P2)
- “Go/No‑Go” recommendation for Shadow Pilot
