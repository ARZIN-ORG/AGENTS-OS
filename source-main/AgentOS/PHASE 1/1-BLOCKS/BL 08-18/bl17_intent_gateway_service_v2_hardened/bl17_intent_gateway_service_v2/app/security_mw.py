# -*- coding: utf-8 -*-
from __future__ import annotations

import time
import hashlib
from typing import Dict, Tuple, Optional

class ReplayGuard:
    """Minimal replay guard for intent creation/finalize calls."""
    def __init__(self, ttl_s: int = 600) -> None:
        self.ttl_s = ttl_s
        self._seen: Dict[str, float] = {}

    def _gc(self) -> None:
        now = time.time()
        dead = [k for k, t in self._seen.items() if now - t > self.ttl_s]
        for k in dead:
            self._seen.pop(k, None)

    def fingerprint(self, actor_id: str, channel: str, body: dict) -> str:
        stable = {"actor_id": actor_id, "channel": channel, "body": body}
        blob = str(stable).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def check_and_mark(self, fp: str) -> Tuple[bool, str]:
        self._gc()
        if fp in self._seen:
            return False, "replay_detected"
        self._seen[fp] = time.time()
        return True, "ok"

class RateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = max(1, per_minute)
        self._hits: Dict[str, Tuple[int, float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        count, start = self._hits.get(key, (0, now))
        if now - start >= 60:
            self._hits[key] = (1, now)
            return True
        if count + 1 > self.per_minute:
            return False
        self._hits[key] = (count + 1, start)
        return True
