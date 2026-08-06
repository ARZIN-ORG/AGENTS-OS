# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from typing import Dict, Tuple

class SimpleRateLimiter:
    """Token-bucket-ish (very small). Replace with gateway-level RL in production."""

    def __init__(self, per_minute: int) -> None:
        self.per_minute = max(1, per_minute)
        self._hits: Dict[str, Tuple[int, float]] = {}  # key -> (count, window_start)

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
