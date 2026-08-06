# -*- coding: utf-8 -*-
"""
SOHA <-> ARZIN AACP Integration Hook Adapter (Phase-1)
File: soha_kafka_hook_adapter_v1.py

- Enforces AACP gates using the wired interceptor (BL-06/07/08).
- Writes audit decision to Audit Sink (BL-08).
- Routes DENY/FAIL-CLOSED to DLQ (BL-02 v2 schema).

No decisions are made here. Enforcement only.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Optional

import requests

from aacp_kafka_manager_PLUG_WIRED_BL08_v1 import build_interceptor, WiredPluginConfig
from aacp_bl02_reject_dlq_v2 import build_dlq_event, publish_dlq, DlqPublisher

def _stable_hash(obj: Dict[str, Any]) -> str:
    b = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()

class AuditSinkClient:
    def __init__(self, base_url: str, timeout_seconds: float = 0.4) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout_seconds
        self._session = requests.Session()

    def write_record(self, record: Dict[str, Any]) -> None:
        url = self._base + "/v1/audit/records"
        resp = self._session.post(url, json=record, timeout=self._timeout, headers={"x-trace-id": record.get("trace_id","")})
        if resp.status_code >= 400:
            raise RuntimeError("audit_sink_rejected")

class SohaKafkaHookAdapter:
    def __init__(
        self,
        *,
        cfg: Optional[WiredPluginConfig] = None,
        audit_sink_base_url: str = "http://audit-sink:8083",
        dlq_publisher: Optional[DlqPublisher] = None,
        dlq_topic: str = "AACP_DLQ",
    ) -> None:
        self._interceptor = build_interceptor(cfg)
        self._audit = AuditSinkClient(audit_sink_base_url)
        self._dlq_pub = dlq_publisher
        self._dlq_topic = dlq_topic

    def on_produce(self, msg: Dict[str, Any], payload_bytes: int) -> Dict[str, Any]:
        env = msg.get("envelope") or {}
        env["payload_bytes"] = int(payload_bytes)

        env["envelope_hash"] = env.get("envelope_hash") or _stable_hash({
            "trace_id": env.get("trace_id"),
            "message_id": env.get("message_id"),
            "channel_id": msg.get("channel_id"),
            "topic": msg.get("topic"),
            "payload_bytes": env.get("payload_bytes"),
            "ttl_seconds": env.get("ttl_seconds"),
            "signature_valid": env.get("signature_valid"),
            "chain_hash": env.get("chain_hash"),
        })
        msg["envelope"] = env

        decision = self._interceptor.intercept(msg)

        record = {
            "trace_id": env.get("trace_id", ""),
            "message_id": env.get("message_id"),
            "channel_id": msg.get("channel_id", ""),
            "topic": msg.get("topic", ""),
            "agent_id": msg.get("agent_id", ""),
            "agent_class": msg.get("agent_class", ""),
            "decision": decision.decision,
            "reason_code": decision.reason,
            "policy_id": decision.policy_id,
            "policy_version": decision.policy_version,
            "signature_valid": bool(env.get("signature_valid", False)),
            "envelope_hash": env.get("envelope_hash"),
            "chain_hash": env.get("chain_hash"),
            "event_time": None,
            "raw": {"hook": "on_produce"},
        }

        # Persist audit first (Fail-Closed discipline)
        self._audit.write_record(record)

        if decision.decision != "ALLOW":
            self._to_dlq(msg, decision.reason, gate=_classify_gate(decision.reason), policy_id=decision.policy_id, policy_version=decision.policy_version)
            raise RuntimeError(f"REJECT:{decision.reason}")

        return msg

    def on_consume(self, msg: Dict[str, Any], payload_bytes: int) -> None:
        self.on_produce(msg, payload_bytes)

    def _to_dlq(self, msg: Dict[str, Any], reason_code: str, gate: str, policy_id: str | None, policy_version: int | None) -> None:
        if self._dlq_pub is None:
            raise RuntimeError("dlq_publisher_missing_fail_closed")

        dlq = build_dlq_event(
            agent_id=str(msg.get("agent_id","")),
            agent_class=str(msg.get("agent_class","")),
            channel_id=str(msg.get("channel_id","")),
            topic=str(msg.get("topic","")),
            envelope=dict(msg.get("envelope") or {}),
            reason_code=reason_code,
            gate=gate,
            policy_id=policy_id,
            policy_version=policy_version,
        )
        publish_dlq(self._dlq_pub, dlq_topic=self._dlq_topic, dlq_event=dlq)

def _classify_gate(reason: str) -> str:
    if reason.startswith("invalid_signature") or "signature" in reason:
        return "signature"
    if "agent_" in reason or "channel_" in reason or "topic_" in reason:
        return "registry"
    if "ttl_" in reason or "payload_" in reason or "decision_class" in reason:
        return "policy"
    if "permit" in reason:
        return "permit"
    if reason.startswith("fail_closed"):
        return "fail_closed"
    return "unknown"
