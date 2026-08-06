# -*- coding: utf-8 -*-
from __future__ import annotations
import hashlib
from typing import Any, Dict, List, Tuple, Optional

def _stable_repr(e: Dict[str, Any]) -> str:
    # Hash only stable bits; tolerates extra fields.
    stable = {
        "ts_utc": e.get("ts_utc"),
        "trace_id": e.get("trace_id"),
        "event_type": e.get("event_type"),
        "actor_id": e.get("actor_id"),
        "action_type": e.get("action_type"),
        "channel": e.get("channel"),
        "decision": e.get("decision"),
        "prev_hash": e.get("prev_hash"),
        "payload": e.get("payload") or {},
    }
    return str(stable)

def compute_hash(e: Dict[str, Any]) -> str:
    blob = _stable_repr(e).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()

def verify_chain(events: List[Dict[str, Any]]) -> Tuple[bool, Optional[int], Optional[str]]:
    """Best-effort chain verification.
    If events contain prev_hash/chain_hash we validate sequentially.
    If missing, we still compute hashes but cannot verify linkage.
    """
    if not events:
        return True, None, None

    for i, e in enumerate(events):
        ch = e.get("chain_hash")
        expected = compute_hash(e)
        if ch and ch != expected:
            return False, i, "chain_hash_mismatch"
        if i > 0:
            prev = events[i-1].get("chain_hash") or compute_hash(events[i-1])
            ph = e.get("prev_hash")
            if ph and ph != prev:
                return False, i, "prev_hash_mismatch"
    return True, None, None
