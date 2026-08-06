from __future__ import annotations

def issue(policy: dict, human_approved: bool) -> dict:
    if not human_approved:
        return {"permit": False, "reason": "Human approval missing"}
    return {"permit": True, "permit_id": "PERMIT-DEFAULT", "policy": policy}
