# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple
import requests

def _mtls_config(prefix: str) -> Tuple[Optional[str], Optional[Tuple[str, str]]]:
    """Returns (verify, cert) for requests.*
    verify: path to CA bundle/cert or True/False
    cert: (client_cert_path, client_key_path) or single pem path
    """
    enabled = os.getenv(f"{prefix}_MTLS_ENABLED", "false").lower() in ("1","true","yes")
    if not enabled:
        return None, None

    ca = os.getenv(f"{prefix}_MTLS_CA_CERT")  # path inside container
    client_cert = os.getenv(f"{prefix}_MTLS_CLIENT_CERT")  # path
    client_key = os.getenv(f"{prefix}_MTLS_CLIENT_KEY")    # path

    verify = ca if ca else True
    cert = None
    if client_cert and client_key:
        cert = (client_cert, client_key)
    elif client_cert:
        cert = client_cert  # combined pem
    return verify, cert

class HttpClient:
    def __init__(self, timeout_s: float, mtls_prefix: str) -> None:
        self.timeout_s = timeout_s
        self.verify, self.cert = _mtls_config(mtls_prefix)

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        kwargs: Dict[str, Any] = {"timeout": self.timeout_s}
        if self.verify is not None:
            kwargs["verify"] = self.verify
        if self.cert is not None:
            kwargs["cert"] = self.cert
        return requests.get(url, params=params, **kwargs)

    def post(self, url: str, json_body: Dict[str, Any]) -> requests.Response:
        kwargs: Dict[str, Any] = {"timeout": self.timeout_s}
        if self.verify is not None:
            kwargs["verify"] = self.verify
        if self.cert is not None:
            kwargs["cert"] = self.cert
        return requests.post(url, json=json_body, **kwargs)

class AuditSinkClient:
    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 4.0) -> None:
        self.base_url = base_url or os.getenv("AUDIT_SINK_URL", "http://audit-sink:8080")
        self.http = HttpClient(timeout_s=timeout_s, mtls_prefix="AUDIT_SINK")

    def health(self) -> Dict[str, Any]:
        r = self.http.get(f"{self.base_url}/health")
        r.raise_for_status()
        return r.json()

    def fetch_events(
        self,
        window_hours: int,
        limit: int = 500,
        actor_id: Optional[str] = None,
        action_type: Optional[str] = None,
        channel: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"window_hours": window_hours, "limit": limit}
        if actor_id:
            params["actor_id"] = actor_id
        if action_type:
            params["action_type"] = action_type
        if channel:
            params["channel"] = channel
        if trace_id:
            params["trace_id"] = trace_id

        r = self.http.get(f"{self.base_url}/v1/events", params=params)
        if r.status_code == 404:
            r = self.http.get(f"{self.base_url}/v1/audit/events", params=params)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
        return data.get("events", [])
