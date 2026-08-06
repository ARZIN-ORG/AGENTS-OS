# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

from .models import PermitDecision

class PermitClient:
    # Calls BL-08 Permit Service. Fail-closed: any error => DENY.
    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 5.0) -> None:
        self.base_url = base_url or os.getenv("AACP_PERMIT_URL", "http://permit-service:8080")
        self.timeout_s = timeout_s

    def request_permit(self, payload: Dict[str, Any]) -> PermitDecision:
        try:
            r = requests.post(f"{self.base_url}/v1/permit", json=payload, timeout=self.timeout_s)
            if r.status_code != 200:
                return PermitDecision(permit_id="n/a", decision="DENY", reason=f"http_{r.status_code}")
            return PermitDecision(**r.json())
        except Exception as e:
            return PermitDecision(permit_id="n/a", decision="DENY", reason=f"error:{type(e).__name__}")
