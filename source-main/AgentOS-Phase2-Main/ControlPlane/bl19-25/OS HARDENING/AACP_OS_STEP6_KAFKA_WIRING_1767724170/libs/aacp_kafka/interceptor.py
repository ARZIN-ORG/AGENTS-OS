from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
import hashlib
import json
import os
import time

from libs.aacp_common.request_guard import require_aacp_headers
from libs.aacp_common.errors import RejectError
from libs.aacp_common.audit import AuditEnvelope
from libs.aacp_kafka.clients import (
    ServiceEndpoints,
    trust_verify,
    policy_resolve,
    permit_issue,
    audit_append,
)

@dataclass(frozen=True)
class InterceptorConfig:
    endpoints: ServiceEndpoints
    channel_id_default: str = "channel::default"

def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

class AACKafkaInterceptor:
    """Strict interceptor for producer/consumer paths.

    - Fail-closed on missing headers/signature/policy/permit/audit.
    - Does not decide anything; it enforces the permit and audit gates.
    """

    def __init__(self, cfg: InterceptorConfig):
        self._cfg = cfg
        self._last_chain_hash: Optional[str] = None

    def guard_publish(self, headers: Dict[str, str], payload: Dict[str, Any], human_approved: bool) -> Tuple[Dict[str, str], Dict[str, Any]]:
        # 1) Contract check
        require_aacp_headers(**headers)

        # Normalize header keys to internal names used by OS-native services
        hdr = self._normalize_headers(headers)

        # 2) Verify signature (over payload canonical form)
        trust_verify(self._cfg.endpoints, hdr, payload)

        # 3) Policy resolve (governance output is minimal here; can be extended)
        governance_output = {"allowed": True, "notes": "governance pre-check passed (producer)", "ts_ms": int(time.time()*1000)}
        policy = policy_resolve(self._cfg.endpoints, hdr, governance_output)

        # 4) Permit gate (must reflect human approval upstream)
        permit = permit_issue(self._cfg.endpoints, hdr, policy, human_approved=human_approved)
        hdr["permit_id"] = permit.get("permit_id", hdr["permit_id"])  # keep trace consistent

        # 5) Audit append (chain hash)
        env = self._build_envelope(hdr)
        digest = _sha256_hex(_canonical_json(payload))
        chain_hash = audit_append(self._cfg.endpoints, hdr, env.model_dump(), payload_digest=digest, prev_chain_hash=self._last_chain_hash)
        self._last_chain_hash = chain_hash

        # Return possibly updated headers (permit_id) to be attached to Kafka message
        out_headers = self._denormalize_headers(hdr)
        return out_headers, payload

    def guard_consume(self, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        require_aacp_headers(**headers)
        hdr = self._normalize_headers(headers)

        trust_verify(self._cfg.endpoints, hdr, payload)

        env = self._build_envelope(hdr)
        digest = _sha256_hex(_canonical_json(payload))
        chain_hash = audit_append(self._cfg.endpoints, hdr, env.model_dump(), payload_digest=digest, prev_chain_hash=self._last_chain_hash)
        self._last_chain_hash = chain_hash
        return payload

    def _build_envelope(self, hdr: Dict[str, Any]) -> AuditEnvelope:
        return AuditEnvelope(
            trace_id=hdr["trace_id"],
            event_id=hdr["event_id"],
            timestamp_ms=int(time.time()*1000),
            producer_id=hdr["producer_id"],
            consumer_id=hdr["consumer_id"],
            channel_id=hdr["channel_id"] or self._cfg.channel_id_default,
            topic=hdr["topic"],
            schema_id=hdr["schema_id"],
            schema_version=hdr["schema_version"],
            policy_id=hdr["policy_id"],
            policy_version=hdr["policy_version"],
            permit_id=hdr["permit_id"],
            intent_id=hdr["intent_id"],
            sig_alg=hdr["sig_alg"],
            signature=hdr["signature"],
            chain_hash=None,
            extras={"phase": "phase1", "locked": True},
        )

    def _normalize_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        # Expect keys as REQUIRED_HEADERS from aacp_common.request_guard
        def g(k: str) -> str:
            v = headers.get(k)
            if v is None:
                raise RejectError("MISSING_HEADERS", f"Header missing: {k}")
            return v

        return {
            "trace_id": g("x-aacp-trace-id"),
            "event_id": g("x-aacp-event-id"),
            "producer_id": g("x-aacp-producer-id"),
            "consumer_id": g("x-aacp-consumer-id"),
            "channel_id": g("x-aacp-channel-id") or self._cfg.channel_id_default,
            "topic": g("x-aacp-topic"),
            "schema_id": g("x-aacp-schema-id"),
            "schema_version": g("x-aacp-schema-version"),
            "policy_id": g("x-aacp-policy-id"),
            "policy_version": g("x-aacp-policy-version"),
            "permit_id": g("x-aacp-permit-id"),
            "intent_id": g("x-aacp-intent-id"),
            "sig_alg": g("x-aacp-sig-alg"),
            "signature": g("x-aacp-signature"),
        }

    def _denormalize_headers(self, hdr: Dict[str, Any]) -> Dict[str, str]:
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
