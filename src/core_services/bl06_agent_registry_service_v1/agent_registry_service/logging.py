# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Logger:
    name: str
    enabled: bool = True

    def _emit(self, level: str, msg: str, **fields: Any) -> None:
        if not self.enabled:
            return
        payload: Dict[str, Any] = {
            "ts": int(time.time() * 1000),
            "logger": self.name,
            "level": level,
            "msg": msg,
            **fields,
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def info(self, msg: str, **fields: Any) -> None:
        self._emit("INFO", msg, **fields)

    def warn(self, msg: str, **fields: Any) -> None:
        self._emit("WARN", msg, **fields)

    def error(self, msg: str, **fields: Any) -> None:
        self._emit("ERROR", msg, **fields)
