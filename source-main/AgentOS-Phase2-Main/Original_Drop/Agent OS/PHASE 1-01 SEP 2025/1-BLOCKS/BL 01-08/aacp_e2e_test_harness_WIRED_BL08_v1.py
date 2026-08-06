# -*- coding: utf-8 -*-
"""
ARZIN / AACP - E2E Wiring Test Harness (Strict) - BL-06/07/08
File: aacp_e2e_test_harness_WIRED_BL08_v1.py

What it does:
- Spins up minimal mock BL-06 Registry, BL-07 Policy Plane, BL-08 Permit endpoints in-process (FastAPI + uvicorn).
- Runs fail-cases + allow-case against AACPKafkaInterceptorWired.
- Validates Fail-Closed semantics and core constraints.

Run:
  pip install fastapi uvicorn requests
  python aacp_e2e_test_harness_WIRED_BL08_v1.py
"""
from __future__ import annotations

import threading
import time
from typing import Any, Dict

from fastapi import FastAPI
import uvicorn

from aacp_kafka_interceptor_PLUG_WIRED_BL08_v1 import AACPKafkaInterceptorWired, InterceptorSettings


def _run_app(app: FastAPI, host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port, log_level="warning")


def make_registry_app() -> FastAPI:
    app = FastAPI()

    @app.get("/v1/agents/{agent_id}")
    def get_agent(agent_id: str) -> Dict[str, Any]:
        if agent_id == "bad-agent":
            return {"agent_id": agent_id, "status": "disabled"}
        return {
            "agent_id": agent_id,
            "status": "active",
            "allowed_channels": ["ch-1"],
            "allowed_topic_prefixes": ["PAYMENT_", "OBS_"],
        }

    return app


def make_policy_app() -> FastAPI:
    app = FastAPI()

    @app.get("/v1/effective-policy")
    def effective_policy(agent_id: str, agent_class: str, channel_id: str, topic: str) -> Dict[str, Any]:
        return {
            "policy_id": "pol-default",
            "active_version": 1,
            "constraints": {
                "decision_classes": ["observe", "recommend"],
                "signature_required": True,
                "max_payload_bytes": 1024,
                "ttl_seconds_min": 1,
                "ttl_seconds_max": 60,
            },
        }

    return app


def make_permit_app() -> FastAPI:
    app = FastAPI()

    @app.post("/v1/permit")
    def permit(payload: Dict[str, Any]) -> Dict[str, Any]:
        env = payload.get("envelope") or {}
        if not env.get("signature_valid"):
            return {"decision": "DENY", "reason": "invalid_signature", "trace_id": env.get("trace_id", "")}
        if payload.get("topic") == "PAYMENT_DENY":
            return {"decision": "DENY", "reason": "policy_deny_topic", "trace_id": env.get("trace_id", "")}
        return {"decision": "ALLOW", "reason": "ok", "policy_id": "pol-default", "policy_version": 1, "trace_id": env.get("trace_id", "")}

    return app


def _start_servers() -> None:
    threads = [
        threading.Thread(target=_run_app, args=(make_registry_app(), "127.0.0.1", 18080), daemon=True),
        threading.Thread(target=_run_app, args=(make_policy_app(), "127.0.0.1", 18081), daemon=True),
        threading.Thread(target=_run_app, args=(make_permit_app(), "127.0.0.1", 18082), daemon=True),
    ]
    for t in threads:
        t.start()
    time.sleep(0.7)


def _make_interceptor() -> AACPKafkaInterceptorWired:
    s = InterceptorSettings(
        registry_base_url="http://127.0.0.1:18080",
        policy_base_url="http://127.0.0.1:18081",
        permit_base_url="http://127.0.0.1:18082",
        http_timeout_seconds=0.4,
        cache_ttl_seconds=1.0,
        cache_max_items=128,
        fail_closed=True,
    )
    return AACPKafkaInterceptorWired(settings=s)


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    _start_servers()
    itc = _make_interceptor()

    base_msg = {
        "agent_id": "agent-1",
        "agent_class": "security",
        "channel_id": "ch-1",
        "topic": "PAYMENT_INITIATED",
        "envelope": {
            "trace_id": "t-1",
            "ttl_seconds": 10,
            "payload_bytes": 100,
            "signature_valid": True,
        },
    }

    d = itc.intercept(dict(base_msg))
    _assert(d.decision == "ALLOW", "allow case should ALLOW")

    m = dict(base_msg)
    m["envelope"] = dict(base_msg["envelope"])
    m["envelope"]["trace_id"] = "t-2"
    m["envelope"]["signature_valid"] = False
    d = itc.intercept(m)
    _assert(d.decision == "DENY" and "invalid_signature" in d.reason, "invalid signature should DENY")

    m = dict(base_msg)
    m["agent_id"] = "bad-agent"
    m["envelope"] = dict(base_msg["envelope"])
    m["envelope"]["trace_id"] = "t-3"
    d = itc.intercept(m)
    _assert(d.decision == "DENY", "disabled agent should DENY")

    m = dict(base_msg)
    m["channel_id"] = "ch-2"
    m["envelope"] = dict(base_msg["envelope"])
    m["envelope"]["trace_id"] = "t-4"
    d = itc.intercept(m)
    _assert(d.decision == "DENY", "channel not allowed should DENY")

    m = dict(base_msg)
    m["envelope"] = dict(base_msg["envelope"])
    m["envelope"]["trace_id"] = "t-5"
    m["envelope"]["payload_bytes"] = 99999
    d = itc.intercept(m)
    _assert(d.decision == "DENY", "payload too large should DENY")

    m = dict(base_msg)
    m["topic"] = "PAYMENT_DENY"
    m["envelope"] = dict(base_msg["envelope"])
    m["envelope"]["trace_id"] = "t-6"
    d = itc.intercept(m)
    _assert(d.decision == "DENY", "permit deny should DENY")

    print("PASS: All wiring tests succeeded.")


if __name__ == "__main__":
    main()
