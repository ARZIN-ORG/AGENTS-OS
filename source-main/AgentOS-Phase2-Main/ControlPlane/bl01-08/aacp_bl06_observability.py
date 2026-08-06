
# -*- coding: utf-8 -*-
"""
BL-06 — Observability (Phase 1)

Goal:
- CTO-grade visibility without vendor lock-in.
- Structured logs with trace_id/message_id.
- Minimal overhead (json dumps only when logging is enabled).

This module is intentionally lightweight.
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

def _now_ms() -> int:
    return int(time.time() * 1000)

def _json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

@dataclass
class Logger:
    name: str
    enabled: bool = True
    stream = sys.stdout

    def info(self, event: str, **fields: Any) -> None:
        if not self.enabled:
            return
        self.stream.write(_json({"ts_ms": _now_ms(), "level": "INFO", "logger": self.name, "event": event, **fields}) + "\n")

    def warn(self, event: str, **fields: Any) -> None:
        if not self.enabled:
            return
        self.stream.write(_json({"ts_ms": _now_ms(), "level": "WARN", "logger": self.name, "event": event, **fields}) + "\n")

    def error(self, event: str, **fields: Any) -> None:
        if not self.enabled:
            return
        self.stream.write(_json({"ts_ms": _now_ms(), "level": "ERROR", "logger": self.name, "event": event, **fields}) + "\n")

def audit_fields(*, trace_id: Optional[str], message_id: Optional[str], channel_id: Optional[str], topic: Optional[str]) -> Dict[str, Any]:
    return {"trace_id": trace_id, "message_id": message_id, "channel_id": channel_id, "topic": topic}
