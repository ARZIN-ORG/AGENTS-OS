# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests

class RecommendationClient:
    def __init__(self, base_url: Optional[str] = None, timeout_s: float = 5.0) -> None:
        self.base_url = base_url or os.getenv("BL13_RECOMMENDATION_URL", "http://recommendation-plane:8080")
        self.timeout_s = timeout_s

    def list_suggestions(self, status: Optional[str] = None) -> Any:
        params = {"status": status} if status else {}
        r = requests.get(f"{self.base_url}/v1/suggestions", params=params, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def get_suggestion(self, suggestion_id: str) -> Any:
        r = requests.get(f"{self.base_url}/v1/suggestions/{suggestion_id}", timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def decide(self, suggestion_id: str, decision_payload: Dict[str, Any]) -> Any:
        r = requests.post(
            f"{self.base_url}/v1/suggestions/{suggestion_id}/decision",
            json=decision_payload,
            timeout=self.timeout_s,
        )
        r.raise_for_status()
        return r.json()
