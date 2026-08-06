
# Permit / Authorization Agent - OS-Native (Mandatory)
# Role: Issues permit only after human approval and policy validation.

class PermitAgent:
    def issue(self, policy: dict, human_approved: bool) -> dict:
        if not human_approved:
            return {"permit": False, "reason": "Human approval missing"}
        return {"permit": True, "policy": policy}
