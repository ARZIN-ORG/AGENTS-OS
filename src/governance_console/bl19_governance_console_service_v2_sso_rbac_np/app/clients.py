# -*- coding: utf-8 -*-
from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
import requests

class HttpClient:
    def __init__(self, timeout_s: float) -> None:
        self.timeout_s = timeout_s

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        return requests.get(url, params=params, timeout=self.timeout_s)

    def post(self, url: str, json_body: Dict[str, Any]) -> requests.Response:
        return requests.post(url, json=json_body, timeout=self.timeout_s)

class AuditSinkClient:
    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 4.0) -> None:
        self.base_url = base_url or os.getenv("AUDIT_SINK_URL", "http://audit-sink:8080")
        self.http = HttpClient(timeout_s)

    def health(self) -> Dict[str, Any]:
        r = self.http.get(f"{self.base_url}/health")
        r.raise_for_status()
        return r.json()

    def fetch_events(self, window_hours: int, limit: int = 500, actor_id: Optional[str] = None,
                     action_type: Optional[str] = None, channel: Optional[str] = None,
                     trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        # Supports compatible audit sink implementations through configured endpoint.
        params = {
            "window_hours": window_hours,
            "limit": limit,
        }
        if actor_id:
            params["actor_id"] = actor_id
        if action_type:
            params["action_type"] = action_type
        if channel:
            params["channel"] = channel
        if trace_id:
            params["trace_id"] = trace_id

        # Convention: /v1/events
        r = self.http.get(f"{self.base_url}/v1/events", params=params)
        if r.status_code == 404:
            # fallback: /v1/audit/events
            r = self.http.get(f"{self.base_url}/v1/audit/events", params=params)
        r.raise_for_status()
        data = r.json()
        # Accept either list or {events:[...]}
        if isinstance(data, list):
            return data
        return data.get("events", [])
