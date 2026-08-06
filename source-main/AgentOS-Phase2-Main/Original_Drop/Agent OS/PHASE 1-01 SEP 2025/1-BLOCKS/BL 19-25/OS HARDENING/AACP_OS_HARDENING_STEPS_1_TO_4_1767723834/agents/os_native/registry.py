from __future__ import annotations

_REGISTRY = {}

def register(agent_id: str, metadata: dict) -> dict:
    _REGISTRY[agent_id] = metadata
    return {"agent_id": agent_id, "registered": True}
