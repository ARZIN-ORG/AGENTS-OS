from __future__ import annotations

def select_channel(intent_type: str) -> str:
    return f"channel::{intent_type}"
