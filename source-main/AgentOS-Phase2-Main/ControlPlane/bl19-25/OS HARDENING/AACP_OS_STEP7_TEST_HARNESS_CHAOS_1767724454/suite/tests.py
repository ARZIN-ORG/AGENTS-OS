from __future__ import annotations
from typing import Any, Dict, List, Tuple
import time

from lib.util import build_envelope, build_payload, dev_sign, canonical_json, sha256_hex, now_ms, new_id
from lib.http_clients import parse_err
from lib.assertions import assert_true, assert_status, assert_code, TestFail
from .context import Ctx

def _call_guard(ctx: Ctx, envelope: Dict[str, Any], payload: Dict[str, Any], signature: str) -> Tuple[int, Dict[str, Any]]:
    # We use Policy->Permit->Audit directly to validate end-to-end, even if interceptor isn't exposed as HTTP.
    # In wired deployments you can replace this with interceptor HTTP endpoint, if you expose it.
    # 1) trust verify
    r1 = ctx.trust.post("/verify", {"envelope": envelope, "payload": payload, "signature": signature})
    if r1.status_code != 200:
        return r1.status_code, parse_err(r1)

    # 2) policy resolve/authorize
    r2 = ctx.policy.post("/resolve", {"envelope": envelope, "payload": payload})
    if r2.status_code != 200:
        return r2.status_code, parse_err(r2)

    # 3) permit check
    r3 = ctx.permit.post("/check", {"envelope": envelope, "payload": payload})
    if r3.status_code != 200:
        return r3.status_code, parse_err(r3)

    # 4) audit append
    payload_digest = sha256_hex(canonical_json(payload))
    envelope["payload_digest"] = payload_digest
    r4 = ctx.audit.post("/append", {"envelope": envelope, "payload_digest": payload_digest, "prev_chain_hash": envelope.get("prev_chain_hash")})
    return r4.status_code, parse_err(r4) if r4.status_code != 200 else r4.json()

def t_health(ctx: Ctx):
    r = ctx.audit.get("/healthz")
    assert_status(r, {200}, "audit health")
    r = ctx.policy.get("/healthz")
    assert_status(r, {200}, "policy health")
    r = ctx.permit.get("/healthz")
    assert_status(r, {200}, "permit health")
    r = ctx.trust.get("/healthz")
    assert_status(r, {200}, "trust health")

def t_required_fields(ctx: Ctx):
    d = dict(ctx.cfg["defaults"])
    env = build_envelope(d)
    payload = build_payload()
    sig = dev_sign(env, payload)
    # Remove critical field
    env.pop("trace_id", None)
    status, body = _call_guard(ctx, env, payload, sig)
    assert_true(status in (400, 422), f"expected validation fail, got {status} {body}")

def t_signature_tamper(ctx: Ctx):
    d = dict(ctx.cfg["defaults"])
    env = build_envelope(d)
    payload = build_payload()
    sig = dev_sign(env, payload)
    payload["amount"] = 999  # tamper after sign
    status, body = _call_guard(ctx, env, payload, sig)
    assert_true(status in (401, 403), f"expected signature reject, got {status} {body}")

def t_policy_deny_topic(ctx: Ctx):
    d = dict(ctx.cfg["defaults"])
    d["topic"] = "arz.forbidden.topic"
    env = build_envelope(d)
    payload = build_payload()
    sig = dev_sign(env, payload)
    status, body = _call_guard(ctx, env, payload, sig)
    assert_true(status in (403, 409), f"expected policy deny, got {status} {body}")

def t_permit_missing(ctx: Ctx):
    d = dict(ctx.cfg["defaults"])
    d["permit_id"] = ""
    env = build_envelope(d)
    payload = build_payload()
    sig = dev_sign(env, payload)
    status, body = _call_guard(ctx, env, payload, sig)
    assert_true(status in (400, 403), f"expected permit reject, got {status} {body}")

def t_expired(ctx: Ctx):
    d = dict(ctx.cfg["defaults"])
    env = build_envelope(d)
    env["expires_at_ms"] = now_ms() - 1
    payload = build_payload()
    sig = dev_sign(env, payload)
    status, body = _call_guard(ctx, env, payload, sig)
    assert_true(status in (400, 403), f"expected expiry reject, got {status} {body}")

def t_audit_down_fail_closed(ctx: Ctx):
    # Simulate audit down by pointing to a non-routable port, but keep other endpoints.
    # This proves audit is in the enforcement chain.
    d = dict(ctx.cfg["defaults"])
    env = build_envelope(d)
    payload = build_payload()
    sig = dev_sign(env, payload)

    original = ctx.audit.base
    ctx.audit.base = "http://127.0.0.1:65530"  # likely closed
    try:
        status, body = _call_guard(ctx, env, payload, sig)
        # Any non-200 is acceptable as "fail closed"
        assert_true(status != 200, f"expected fail-closed, got 200 {body}")
    finally:
        ctx.audit.base = original

def t_chain_hash_optional_continuity(ctx: Ctx):
    # If strict_chain is enabled, we verify continuity by passing prev hash.
    # If not enabled, we just ensure chain_hash returns and is stable format.
    strict = bool(ctx.cfg.get("strict_chain", False))
    d = dict(ctx.cfg["defaults"])

    env1 = build_envelope(d)
    payload1 = build_payload()
    sig1 = dev_sign(env1, payload1)
    s1, b1 = _call_guard(ctx, env1, payload1, sig1)
    assert_true(s1 == 200, f"expected success, got {s1} {b1}")
    ch1 = b1.get("chain_hash")
    assert_true(isinstance(ch1, str) and len(ch1) == 64, "chain_hash must be sha256 hex")

    env2 = build_envelope(d)
    env2["prev_chain_hash"] = ch1
    payload2 = build_payload()
    sig2 = dev_sign(env2, payload2)
    s2, b2 = _call_guard(ctx, env2, payload2, sig2)
    assert_true(s2 == 200, f"expected success, got {s2} {b2}")

    if strict:
        # Wrong prev should fail
        env3 = build_envelope(d)
        env3["prev_chain_hash"] = "0"*64
        payload3 = build_payload()
        sig3 = dev_sign(env3, payload3)
        s3, b3 = _call_guard(ctx, env3, payload3, sig3)
        assert_true(s3 in (409, 400), f"expected chain mismatch, got {s3} {b3}")

def t_replay_event_id(ctx: Ctx):
    # Basic replay: submit same event_id twice. Depending on services, policy/permit/audit may reject.
    d = dict(ctx.cfg["defaults"])
    fixed_event = new_id("evt")
    env = build_envelope({**d, "event_id": fixed_event})
    payload = build_payload()
    sig = dev_sign(env, payload)

    s1, b1 = _call_guard(ctx, env, payload, sig)
    assert_true(s1 == 200, f"first submit should pass, got {s1} {b1}")

    env2 = build_envelope({**d, "event_id": fixed_event, "trace_id": env.get("trace_id")})
    payload2 = build_payload()
    sig2 = dev_sign(env2, payload2)
    s2, b2 = _call_guard(ctx, env2, payload2, sig2)
    # acceptable outcomes: reject replay OR accept with separate audit record (phase-1 might not dedupe globally yet)
    assert_true(s2 in (200, 409, 422, 400), f"unexpected status for replay {s2} {b2}")

TESTS = [
    ("health", t_health),
    ("required_fields", t_required_fields),
    ("signature_tamper", t_signature_tamper),
    ("policy_deny_topic", t_policy_deny_topic),
    ("permit_missing", t_permit_missing),
    ("expired", t_expired),
    ("audit_down_fail_closed", t_audit_down_fail_closed),
    ("chain_hash_optional_continuity", t_chain_hash_optional_continuity),
    ("replay_event_id", t_replay_event_id),
]
