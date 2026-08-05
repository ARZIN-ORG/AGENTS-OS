cat > README.md <<'EOF'
# ZINOVA Agent Operating System

Claude-native agent operating model for ZINOVA.

## Core Rules

1. Agents do not make final decisions.
2. All design and implementation follow the Claude-native operating model.
3. No mock or fabricated execution is permitted.

## Architecture

```text
.claude/
    agents/
    commands/
    skills/

governance/
committee/
workflows/
decisions/
audit/
identities/
Decision Model
Agent
  ↓
Analysis / Challenge
  ↓
Recommendation
  ↓
Executive Decision Package
  ↓
Executive Committee
  ↓
Approve / Reject / Return
  ↓
Authorized Execution
Executive Committee
Founder
CEO
CTO
Executive Manager
Agents are advisory systems.
The Executive Committee owns final decision authority.
