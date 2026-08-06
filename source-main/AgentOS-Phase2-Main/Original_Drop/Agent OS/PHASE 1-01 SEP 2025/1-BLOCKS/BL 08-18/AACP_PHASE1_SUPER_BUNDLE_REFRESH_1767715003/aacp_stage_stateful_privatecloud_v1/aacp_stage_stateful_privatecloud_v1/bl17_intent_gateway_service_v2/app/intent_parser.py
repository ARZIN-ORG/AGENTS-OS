# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, Tuple

def parse_intent(text: str) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
    """Phase-1 deterministic intent parser.

    This is intentionally conservative.
    It produces a draft that must be human-reviewed before execution.

    Output:
      action_type, target, parameters
    """
    t = text.strip().lower()

    # Very small starter vocabulary; extend via policy later.
    if "stop" in t and "agent" in t:
        return "STOP_AGENT", {"kind": "agent"}, {"reason": "manual_request"}
    if "start" in t and "agent" in t:
        return "START_AGENT", {"kind": "agent"}, {"reason": "manual_request"}
    if "close" in t and "channel" in t:
        return "CLOSE_CHANNEL", {"kind": "channel"}, {"mode": "graceful"}
    if "open" in t and "channel" in t:
        return "OPEN_CHANNEL", {"kind": "channel"}, {"mode": "graceful"}

    # Default: analysis/report request (non-operational)
    return "MANAGEMENT_REPORT", {"kind": "report"}, {"scope": "default"}
