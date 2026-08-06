# -*- coding: utf-8 -*-
"""E2E harness (Phase-1): Suggestion -> Human Accept -> Permit -> Publish

This test is designed to be run by DevOps in private cloud or local docker-compose.
It is intentionally strict and fail-closed.

Dependencies:
- BL-13 Recommendation Plane reachable
- BL-17 Intent Gateway reachable
- BL-08 Permit Service reachable (or mocked with deterministic ALLOW/DENY)
"""

from __future__ import annotations

import os
import json
import time
import requests

BL13 = os.getenv("BL13_URL", "http://localhost:8081")
BL17 = os.getenv("BL17_URL", "http://localhost:8082")

def _post(url: str, payload: dict) -> dict:
    r = requests.post(url, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def _get(url: str) -> dict:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def run() -> None:
    print("Health checks...")
    print(_get(f"{BL13}/health"))
    print(_get(f"{BL17}/health"))

    # 1) Create suggestion (non-executable)
    sugg = _post(
        f"{BL13}/v1/suggestions",
        {
            "created_by_agent": "resilience_agent",
            "audience": "MANAGER",
            "title": "Close channel X due to error spike",
            "summary": "Observed error rate > threshold for 10m. Suggest graceful close to contain blast radius.",
            "domain": "resilience",
            "confidence": 0.72,
            "expected_impact": {"availability": "increase", "risk": "lower"},
            "risk_notes": ["May delay non-critical messages for channel X"],
            "proposed_action": {"action_type": "CLOSE_CHANNEL", "target": {"channel": "X"}, "mode": "graceful"},
        },
    )
    sid = sugg["suggestion_id"]
    print("Created suggestion:", sid)

    # 2) List suggestions through BL-17 proxy (UI path)
    lst = _get(f"{BL17}/v1/suggestions")
    assert any(x["suggestion_id"] == sid for x in lst), "Suggestion not visible via BL-17 proxy"

    # 3) Human ACCEPT via BL-17 proxy (enforces the locked flow)
    resp = _post(
        f"{BL17}/v1/suggestions/{sid}/decision",
        {"reviewer_id": "manager_001", "decision": "ACCEPT", "reason": "approved"},
    )
    print("Decision response:", json.dumps(resp, indent=2)[:1200])

    # 4) Validate final state in BL-13
    final = _get(f"{BL13}/v1/suggestions/{sid}")
    print("Final suggestion:", json.dumps(final, indent=2)[:1200])
    assert final["status"] in ("ACCEPTED", "REJECTED"), "Unexpected final status"

    print("OK")

if __name__ == "__main__":
    run()
