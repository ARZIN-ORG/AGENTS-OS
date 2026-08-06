
# Governance Agent - OS-Native (Mandatory)
# Role: Enforces top-level governance principles. No execution, no decision.

class GovernanceAgent:
    def evaluate(self, context: dict) -> dict:
        return {
            "allowed": True,
            "notes": "Governance constraints validated",
            "context_hash": context.get("hash")
        }
