from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import json
import urllib.request
import urllib.error

from libs.aacp_common.errors import RejectError

@dataclass(frozen=True)
class ServiceEndpoints:
    trust_url: str
    policy_url: str
    permit_url: str
    audit_url: str

def _post_json(url: str, path: str, body: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout_s: int = 5) -> Dict[str, Any]:
    full = url.rstrip("/") + path
    data = json.dumps(body, separators=(",", ":"), sort_keys=True).encode("utf-8")
    req = urllib.request.Request(full, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="ignore")
        raise RejectError("UPSTREAM_HTTP_ERROR", f"{full} -> {e.code}: {msg}")
    except Exception as e:
        raise RejectError("UPSTREAM_UNREACHABLE", f"{full} -> {type(e).__name__}: {e}")

def trust_verify(endpoints: ServiceEndpoints, hdr: Dict[str, Any], message: Dict[str, Any]) -> bool:
    out = _post_json(endpoints.trust_url, "/verify", {"message": message, "signature_hex": hdr["signature"]}, headers=_aacp_hdrs(hdr))
    ok = bool(out.get("verified"))
    if not ok:
        raise RejectError("SIGNATURE_INVALID", "Signature verification failed")
    return True

def policy_resolve(endpoints: ServiceEndpoints, hdr: Dict[str, Any], governance_output: Dict[str, Any]) -> Dict[str, Any]:
    out = _post_json(endpoints.policy_url, "/resolve", {"governance_output": governance_output}, headers=_aacp_hdrs(hdr))
    policy = out.get("policy")
    if not isinstance(policy, dict) or not policy.get("policy_id"):
        raise RejectError("POLICY_RESOLVE_FAILED", "Policy plane returned invalid policy")
    return policy

def permit_issue(endpoints: ServiceEndpoints, hdr: Dict[str, Any], policy: Dict[str, Any], human_approved: bool) -> Dict[str, Any]:
    out = _post_json(endpoints.permit_url, "/issue", {"policy": policy, "human_approved": bool(human_approved)}, headers=_aacp_hdrs(hdr))
    permit = out.get("permit")
    if not isinstance(permit, dict):
        raise RejectError("PERMIT_FAILED", "Permit service returned invalid response")
    if not permit.get("permit"):
        raise RejectError("PERMIT_DENIED", permit.get("reason", "Permit denied"))
    return permit

def audit_append(endpoints: ServiceEndpoints, hdr: Dict[str, Any], envelope: Dict[str, Any], payload_digest: Optional[str], prev_chain_hash: Optional[str]) -> str:
    out = _post_json(endpoints.audit_url, "/append", {"envelope": envelope, "payload_digest": payload_digest, "prev_chain_hash": prev_chain_hash}, headers=_aacp_hdrs(hdr))
    if not out.get("ok"):
        raise RejectError("AUDIT_APPEND_FAILED", "Audit sink failed to append")
    chain_hash = out.get("chain_hash")
    if not chain_hash:
        raise RejectError("AUDIT_CHAINHASH_MISSING", "Audit sink did not return chain_hash")
    return str(chain_hash)

def _aacp_hdrs(hdr: Dict[str, Any]) -> Dict[str, str]:
    # Pass-through for traceability
    return {
        "x-aacp-trace-id": hdr["trace_id"],
        "x-aacp-event-id": hdr["event_id"],
        "x-aacp-producer-id": hdr["producer_id"],
        "x-aacp-consumer-id": hdr["consumer_id"],
        "x-aacp-channel-id": hdr["channel_id"],
        "x-aacp-topic": hdr["topic"],
        "x-aacp-schema-id": hdr["schema_id"],
        "x-aacp-schema-version": hdr["schema_version"],
        "x-aacp-policy-id": hdr["policy_id"],
        "x-aacp-policy-version": hdr["policy_version"],
        "x-aacp-permit-id": hdr["permit_id"],
        "x-aacp-intent-id": hdr["intent_id"],
        "x-aacp-sig-alg": hdr["sig_alg"],
        "x-aacp-signature": hdr["signature"],
    }
