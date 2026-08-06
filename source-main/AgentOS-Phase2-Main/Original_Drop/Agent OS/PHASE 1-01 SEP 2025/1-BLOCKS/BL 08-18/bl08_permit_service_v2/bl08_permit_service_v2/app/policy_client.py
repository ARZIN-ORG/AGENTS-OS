# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, Optional
import requests

class PolicyClient:
    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 4.0) -> None:
        self.base_url = base_url or os.getenv("POLICY_PLANE_URL", "http://policy-plane:8080")
        self.timeout_s = timeout_s

    def resolve(self, actor_id: str, action_type: str, channel: str, scope: Optional[str]) -> Dict[str, Any]:
        payload = {
            "actor_id": actor_id,
            "action_type": action_type,
            "channel": channel,
            "scope": scope or "default",
        }
        r = requests.post(f"{self.base_url}/v1/policy/resolve", json=payload, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()
