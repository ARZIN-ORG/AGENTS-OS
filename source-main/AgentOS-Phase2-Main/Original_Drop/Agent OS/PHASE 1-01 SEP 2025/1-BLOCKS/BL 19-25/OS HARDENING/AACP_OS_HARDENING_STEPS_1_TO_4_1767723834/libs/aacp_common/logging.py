from __future__ import annotations
import json
import time
from typing import Any, Dict

def log_event(kind: str, data: Dict[str, Any]) -> str:
    payload = {"ts_ms": int(time.time()*1000), "kind": kind, **data}
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
