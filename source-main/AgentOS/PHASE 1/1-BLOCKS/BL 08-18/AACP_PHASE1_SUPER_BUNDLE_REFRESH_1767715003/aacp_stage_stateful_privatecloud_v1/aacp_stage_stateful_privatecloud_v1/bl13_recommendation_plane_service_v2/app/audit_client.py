# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, Optional
import requests

class AuditClient:
    """Emit audit records to BL-08 Audit Sink.

    Non-fatal: if audit sink is down, we do NOT execute or publish.
    For BL-13, audit failure should fail the decision path (strict mode) to preserve governance.
    """

    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 5.0) -> None:
        self.base_url = base_url or os.getenv("AACP_AUDIT_SINK_URL", "http://audit-sink:8080")
        self.timeout_s = timeout_s
        self.strict = os.getenv("AACP_AUDIT_STRICT", "true").lower() in ("1", "true", "yes")

    def emit_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/v1/audit/records", json=record, timeout=self.timeout_s)
            if r.status_code != 200:
                if self.strict:
                    raise RuntimeError(f"audit_http_{r.status_code}")
                return {"ok": False, "mode": "non_strict", "status": r.status_code}
            return {"ok": True, "record": r.json()}
        except Exception as e:
            if self.strict:
                raise
            return {"ok": False, "mode": "non_strict", "error": type(e).__name__}
