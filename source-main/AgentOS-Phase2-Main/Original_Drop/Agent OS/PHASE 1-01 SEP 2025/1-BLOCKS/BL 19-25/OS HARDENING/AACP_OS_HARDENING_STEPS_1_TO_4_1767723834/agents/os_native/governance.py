from __future__ import annotations

def evaluate(context: dict) -> dict:
    # Advisory governance check — no execution.
    return {"allowed": True, "notes": "Governance constraints validated", "context_hash": context.get("hash")}
