# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Tuple

class InMemoryReplayGuard:
    """Phase-1 minimal replay guard. Replace with Redis for HA."""

    def __init__(self, ttl_s: int = 600) -> None:
        self.ttl_s = ttl_s
        self._seen: Dict[str, float] = {}

    def _gc(self) -> None:
        now = time.time()
        dead = [k for k, t in self._seen.items() if now - t > self.ttl_s]
        for k in dead:
            self._seen.pop(k, None)

    def fingerprint(self, req: Dict[str, Any]) -> str:
        # Only stable fields included (exclude parameters that can be noisy if desired)
        stable = {
            "requested_by": req.get("requested_by"),
            "requested_at_utc": req.get("requested_at_utc"),
            "action_type": req.get("action_type"),
            "channel": req.get("channel"),
            "scope": req.get("scope"),
            "request_id": req.get("request_id"),
            "target": req.get("target") or {},
        }
        blob = str(stable).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def check_and_mark(self, fp: str) -> Tuple[bool, str]:
        self._gc()
        if fp in self._seen:
            return False, "replay_detected"
        self._seen[fp] = time.time()
        return True, "ok"
