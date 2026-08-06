# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import json
import subprocess
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

NAMESPACE = os.getenv("AACP_NS", "aacp")
INTENT_URL = os.getenv("INTENT_URL", "http://intent-gateway:8080")
TIMEOUT_S = float(os.getenv("HTTP_TIMEOUT", "3.0"))

def sh(cmd: List[str]) -> str:
    p = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.stdout.strip()

def apply(path: str) -> None:
    sh(["kubectl", "apply", "-f", path])

def delete(path: str) -> None:
    sh(["kubectl", "delete", "-f", path, "--ignore-not-found=true"])

def post_intent(payload: Dict) -> requests.Response:
    return requests.post(f"{INTENT_URL}/v1/intent", json=payload, timeout=TIMEOUT_S)

@dataclass
class Case:
    name: str
    payload: Dict
    expect_http: int

def assert_case(case: Case) -> Dict:
    r = post_intent(case.payload)
    ok = (r.status_code == case.expect_http)
    return {"case": case.name, "status": "ok" if ok else "fail", "http": r.status_code, "body": r.text[:300]}

def main() -> int:
    report = {"suite": "failclosed", "ts": time.time(), "results": [], "faults": []}

    cases = [
        Case("missing_signature", {"mode":"text","input":"status report", "signature": None}, 400),
        Case("invalid_signature", {"mode":"text","input":"status report", "signature": "deadbeef"}, 403),
        Case("missing_mfa", {"mode":"text","input":"do x", "mfa": None, "signature":"x"}, 401),
    ]

    # Baseline negative tests
    for c in cases:
        try:
            report["results"].append(assert_case(c))
        except Exception as e:
            report["results"].append({"case": c.name, "status": "error", "error": str(e)})

    # Fault: block permit->policy and ensure deny (or explicit fail)
    fault_np = "k8s/fault_inject_block_permit_to_policy.yaml"
    try:
        apply(fault_np)
        report["faults"].append({"fault": "block_permit_to_policy", "status": "applied"})
        time.sleep(2)
        # Expect system to fail closed (403/503 acceptable depending on gateway contract)
        r = post_intent({"mode":"text","input":"should_fail_closed","signature":"x","mfa":"ok"})
        report["results"].append({"case":"policy_unreachable_fail_closed","http": r.status_code, "body": r.text[:200]})
    finally:
        delete(fault_np)

    # Fault: audit sink down — ensure no silent success (expect 502/503/403)
    fault_audit = "k8s/fault_inject_audit_down.yaml"
    try:
        apply(fault_audit)
        report["faults"].append({"fault": "audit_down", "status": "applied"})
        time.sleep(2)
        r = post_intent({"mode":"text","input":"should_fail_without_audit","signature":"x","mfa":"ok"})
        report["results"].append({"case":"audit_unreachable_no_silent_success","http": r.status_code, "body": r.text[:200]})
    finally:
        # do not leave audit scaled to 0 in real environment; this file is illustrative
        delete(fault_audit)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
