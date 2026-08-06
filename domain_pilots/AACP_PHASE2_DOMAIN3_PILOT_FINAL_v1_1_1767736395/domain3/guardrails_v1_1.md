
# Execution & Governance Guardrails (v1.1)

1) Evidence Gate (Mandatory)
Any insight/narrative line must reference evidence IDs. Otherwise: REJECT.

2) Visibility Gate (Mandatory)
Pilot outputs visible ONLY in Governance Console Executive Mode.
No broadcast/export without Governance approval.

3) Safety Gate (Mandatory)
No instructions that resemble operational commands.
No direct routing/publishing to AACP topics.

4) Integrity Gate (Mandatory)
All inputs must pass Signature Verification and match Registry ownership.

5) Drift Gate (Mandatory)
If Policy Version changes during generation -> invalidate and regenerate.
