# ZINOVA Agent Operating System

## Purpose

This repository defines the Claude-native operating model for building and operating ZINOVA as an agent-based organization.

Claude is the operating platform for agent definitions, skills, commands, workflows, governance enforcement and agent collaboration.

---

# FOUNDATIONAL RULES

## Rule 01 — Agent Decision Authority

Agents do not make final organizational, strategic, financial, technical or operational decisions.

Agents may:

- analyze
- investigate
- evaluate
- challenge
- identify risks
- generate alternatives
- prepare recommendations
- prepare decision packages

Agents must submit their recommendations and proposed conclusions to the Executive Committee.

Final authority belongs exclusively to the Executive Committee:

- Founder
- CEO
- CTO
- Executive Manager

An agent recommendation is not a decision.

An agent conclusion is not an approval.

An agent output cannot authorize execution.

---

## Rule 02 — Claude-Native Operating Model

All design, implementation, architecture, workflows, agent behavior, skills, commands and operational thinking for this repository are based on the Claude platform and its native operating model.

The `.claude/` directory is the authoritative Claude runtime configuration.

Do not introduce an alternative agent runtime architecture unless explicitly authorized by the Executive Committee.

---

## Rule 03 — No Mock Execution

Nothing in this repository may be created, demonstrated or validated through mock, fake, simulated or fabricated execution.

No:

- mock agent
- fake agent response
- fake approval
- simulated decision
- fabricated execution result
- placeholder execution presented as real
- artificial success evidence

may be used as proof of system functionality.

Documentation and schemas may describe future behavior, but they must never be represented as actual execution.

Validation must use the real Claude execution path and real repository artifacts.

---

# AUTHORITY MODEL

Agent
  ↓
Analysis / Challenge / Recommendation
  ↓
Executive Decision Package
  ↓
Executive Committee
  ↓
Approve / Reject / Return
  ↓
Authorized execution

Agents cannot bypass the Executive Committee.

---

# AGENT OPERATING PRINCIPLES

Every agent must:

1. Know its role.
2. Stay within its authority.
3. Base conclusions on available evidence.
4. Identify uncertainty.
5. Distinguish facts from assumptions.
6. Produce traceable recommendations.
7. Escalate decisions outside its authority.
8. Never represent a recommendation as an approved decision.

---

# REPOSITORY MODEL

.claude/
    Claude-native runtime configuration

governance/
    Organizational governance and authority rules

committee/
    Executive Committee authority and decision records

workflows/
    Organizational process definitions

decisions/
    Decision packages and decision history

audit/
    Evidence and audit trail

---

# SOURCE OF TRUTH

CLAUDE.md
    ↓
Governance
    ↓
Agent definitions
    ↓
Skills / Commands
    ↓
Workflows
    ↓
Decision packages
    ↓
Executive Committee
    ↓
Authorized execution
