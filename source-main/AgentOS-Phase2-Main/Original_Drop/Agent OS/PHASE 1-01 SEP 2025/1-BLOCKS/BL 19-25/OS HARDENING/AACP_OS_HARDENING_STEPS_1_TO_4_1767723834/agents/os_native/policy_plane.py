from __future__ import annotations

def resolve(governance_output: dict) -> dict:
    return {"policy_id": "POLICY-DEFAULT", "policy_version": "1", "constraints": governance_output}
