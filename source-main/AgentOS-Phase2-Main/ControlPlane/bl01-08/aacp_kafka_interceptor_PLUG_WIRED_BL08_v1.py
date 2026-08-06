# -*- coding: utf-8 -*-
"""
ARZIN / AACP - Kafka Interceptor Plugin (Wired) - BL-06/07/08
File: aacp_kafka_interceptor_PLUG_WIRED_BL08_v1.py

Phase-1 Guarantees (Locked):
- No agent makes decisions. This component only enforces governance gates (observe/recommend only).
- Fail-Closed: timeout/unavailable downstream control-plane services => REJECT
- Private Cloud: no external deps beyond configured internal service URLs
- End-to-End auditability: emit structured decision events (caller integrates with BL-08 Audit Sink)

This interceptor is designed to be embedded into a Kafka producer/consumer pipeline as a strict gate.
It does not assume Kafka internals; it provides a simple "intercept()" decision API.

NOTE:
- Actual Kafka hook glue depends on your runtime (Java interceptor, Python wrapper, sidecar, etc.).
- This file is governance logic and wiring only. No "execute" actions exist here by design.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


class RejectException(RuntimeError):
    pass


@dataclass(frozen=True)
class InterceptorSettings:
    registry_base_url: str
    policy_base_url: str
    permit_base_url: str

    http_timeout_seconds: float = 0.35  # tight to protect data plane
    http_retries: int = 0               # retries are risky for hot path; keep 0 in phase1
    cache_ttl_seconds: float = 2.0      # short TTL to reduce staleness
    cache_max_items: int = 2048

    fail_closed: bool = True


@dataclass
class AACPDecision:
    decision: str  # "ALLOW" | "DENY"
    reason: str
    trace_id: str
    policy_id: Optional[str] = None
    policy_version: Optional[int] = None


class _TTLCache:
    def __init__(self, ttl_seconds: float, max_items: int) -> None:
        self._ttl = float(ttl_seconds)
        self._max = int(max_items)
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        item = self._store.get(key)
        if not item:
            return None
        ts, val = item
        if (now - ts) > self._ttl:
            self._store.pop(key, None)
            return None
        return val

    def put(self, key: str, val: Any) -> None:
        if len(self._store) >= self._max:
            self._store.pop(next(iter(self._store.keys())), None)
        self._store[key] = (time.time(), val)


class AACPKafkaInterceptorWired:
    """
    Expected input "message" shape:
      {
        "agent_id": str,
        "agent_class": str,
        "channel_id": str,
        "topic": str,
        "envelope": {
          "trace_id": str,
          "ttl_seconds": int,
          "payload_bytes": int,
          "signature_valid": bool,
          "chain_hash": str|None,
          "message_id": str|None
        }
      }
    """
    def __init__(self, settings: InterceptorSettings) -> None:
        self._s = settings
        self._registry_cache = _TTLCache(settings.cache_ttl_seconds, settings.cache_max_items)
        self._policy_cache = _TTLCache(settings.cache_ttl_seconds, settings.cache_max_items)
        self._permit_cache = _TTLCache(settings.cache_ttl_seconds, settings.cache_max_items)
        self._session = requests.Session()

    def intercept(self, message: Dict[str, Any]) -> AACPDecision:
        try:
            self._validate_minimum(message)
            agent_id = str(message["agent_id"])
            agent_class = str(message["agent_class"])
            channel_id = str(message["channel_id"])
            topic = str(message["topic"])
            env = dict(message["envelope"])
            trace_id = str(env["trace_id"])

            # Envelope hard rules (Phase1 Fail-Closed)
            if not bool(env.get("signature_valid", False)):
                return AACPDecision("DENY", "invalid_signature", trace_id=trace_id)

            ttl = int(env.get("ttl_seconds", 0))
            if ttl <= 0:
                return AACPDecision("DENY", "ttl_expired_or_missing", trace_id=trace_id)

            payload_bytes = int(env.get("payload_bytes", -1))
            if payload_bytes < 0:
                return AACPDecision("DENY", "payload_bytes_missing", trace_id=trace_id)

            # BL-06 Registry (fail closed)
            reg = self._registry_lookup(agent_id=agent_id, trace_id=trace_id)
            self._enforce_registry(reg, agent_id, channel_id, topic)

            # BL-07 Effective Policy (fail closed)
            eff = self._policy_lookup(agent_id=agent_id, agent_class=agent_class, channel_id=channel_id, topic=topic, trace_id=trace_id)
            self._enforce_policy_constraints(eff, env)

            # BL-08 Permit (fail closed)
            permit = self._permit_decide(agent_id=agent_id, agent_class=agent_class, channel_id=channel_id, topic=topic, env=env, trace_id=trace_id)
            if permit.get("decision") != "ALLOW":
                return AACPDecision("DENY", str(permit.get("reason", "permit_denied")), trace_id=trace_id)

            return AACPDecision(
                "ALLOW",
                "permit_allow",
                trace_id=trace_id,
                policy_id=permit.get("policy_id"),
                policy_version=permit.get("policy_version"),
            )
        except Exception as e:
            if self._s.fail_closed:
                trace_id = ""
                try:
                    trace_id = str(message.get("envelope", {}).get("trace_id", ""))
                except Exception:
                    trace_id = ""
                return AACPDecision("DENY", f"fail_closed:{type(e).__name__}", trace_id=trace_id or "unknown")
            raise

    def _validate_minimum(self, msg: Dict[str, Any]) -> None:
        for k in ("agent_id", "agent_class", "channel_id", "topic", "envelope"):
            if k not in msg:
                raise ValueError(f"missing_field:{k}")
        env = msg["envelope"]
        for k in ("trace_id", "ttl_seconds", "payload_bytes", "signature_valid"):
            if k not in env:
                raise ValueError(f"missing_envelope_field:{k}")

    def _registry_lookup(self, agent_id: str, trace_id: str) -> Dict[str, Any]:
        cache_key = f"reg::{agent_id}"
        cached = self._registry_cache.get(cache_key)
        if cached is not None:
            return cached
        url = self._s.registry_base_url.rstrip("/") + f"/v1/agents/{agent_id}"
        reg = self._http_get_json(url, trace_id=trace_id)
        self._registry_cache.put(cache_key, reg)
        return reg

    def _policy_lookup(self, agent_id: str, agent_class: str, channel_id: str, topic: str, trace_id: str) -> Dict[str, Any]:
        cache_key = f"pol::{agent_id}::{agent_class}::{channel_id}::{topic}"
        cached = self._policy_cache.get(cache_key)
        if cached is not None:
            return cached
        url = self._s.policy_base_url.rstrip("/") + "/v1/effective-policy"
        params = {"agent_id": agent_id, "agent_class": agent_class, "channel_id": channel_id, "topic": topic}
        eff = self._http_get_json(url, params=params, trace_id=trace_id)
        self._policy_cache.put(cache_key, eff)
        return eff

    def _permit_decide(self, agent_id: str, agent_class: str, channel_id: str, topic: str, env: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        msg_id = str(env.get("message_id") or trace_id)
        cache_key = f"permit::{msg_id}"
        cached = self._permit_cache.get(cache_key)
        if cached is not None:
            return cached
        url = self._s.permit_base_url.rstrip("/") + "/v1/permit"
        payload: Dict[str, Any] = {
            "agent_id": agent_id,
            "agent_class": agent_class,
            "channel_id": channel_id,
            "topic": topic,
            "envelope": {
                "trace_id": trace_id,
                "ttl_seconds": int(env.get("ttl_seconds", 0)),
                "payload_bytes": int(env.get("payload_bytes", 0)),
                "signature_valid": bool(env.get("signature_valid", False)),
            },
        }
        if env.get("chain_hash"):
            payload["envelope"]["chain_hash"] = str(env["chain_hash"])
        decision = self._http_post_json(url, payload=payload, trace_id=trace_id)
        self._permit_cache.put(cache_key, decision)
        return decision

    def _enforce_registry(self, reg: Dict[str, Any], agent_id: str, channel_id: str, topic: str) -> None:
        status = str(reg.get("status", "")).lower()
        if status not in ("active", "enabled"):
            raise RejectException(f"agent_not_active:{agent_id}")

        allowed_channels = reg.get("allowed_channels") or []
        if allowed_channels and channel_id not in allowed_channels:
            raise RejectException(f"channel_not_allowed:{channel_id}")

        allowed_topics = reg.get("allowed_topics") or []
        allowed_prefixes = reg.get("allowed_topic_prefixes") or []
        if allowed_topics or allowed_prefixes:
            ok = (topic in allowed_topics) or any(topic.startswith(p) for p in allowed_prefixes)
            if not ok:
                raise RejectException(f"topic_not_allowed:{topic}")

    def _enforce_policy_constraints(self, eff: Dict[str, Any], env: Dict[str, Any]) -> None:
        constraints = eff.get("constraints") or {}

        dcs = constraints.get("decision_classes") or []
        for dc in dcs:
            if dc not in ("observe", "recommend"):
                raise RejectException(f"decision_class_not_allowed:{dc}")

        if constraints.get("signature_required") is not True:
            raise RejectException("signature_required_false")

        max_bytes = int(constraints.get("max_payload_bytes", 1048576))
        pb = int(env.get("payload_bytes", 0))
        if pb > max_bytes:
            raise RejectException("payload_too_large")

        ttl_min = int(constraints.get("ttl_seconds_min", 1))
        ttl_max = int(constraints.get("ttl_seconds_max", 300))
        ttl = int(env.get("ttl_seconds", 0))
        if ttl < ttl_min or ttl > ttl_max:
            raise RejectException("ttl_out_of_bounds")

    def _http_get_json(self, url: str, params: Optional[Dict[str, Any]] = None, trace_id: str = "") -> Dict[str, Any]:
        headers = {"x-trace-id": trace_id} if trace_id else {}
        resp = self._session.get(url, params=params, timeout=self._s.http_timeout_seconds, headers=headers)
        if resp.status_code >= 400:
            raise RejectException(f"http_get_failed:{resp.status_code}")
        return resp.json()

    def _http_post_json(self, url: str, payload: Dict[str, Any], trace_id: str = "") -> Dict[str, Any]:
        headers = {"content-type": "application/json"}
        if trace_id:
            headers["x-trace-id"] = trace_id
        resp = self._session.post(url, data=json.dumps(payload), timeout=self._s.http_timeout_seconds, headers=headers)
        if resp.status_code >= 400:
            raise RejectException(f"http_post_failed:{resp.status_code}")
        return resp.json()
