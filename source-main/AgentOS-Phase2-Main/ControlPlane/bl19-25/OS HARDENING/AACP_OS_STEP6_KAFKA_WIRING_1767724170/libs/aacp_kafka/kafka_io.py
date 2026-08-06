from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Callable, Optional
import os
import time
import uuid
import json
import hmac
import hashlib

from libs.aacp_kafka.clients import ServiceEndpoints
from libs.aacp_kafka.interceptor import InterceptorConfig, AACKafkaInterceptor

def _hmac_sha256_hex(secret: bytes, message: bytes) -> str:
    return hmac.new(secret, message, hashlib.sha256).hexdigest()

@dataclass(frozen=True)
class AACPEnv:
    trust_url: str
    policy_url: str
    permit_url: str
    audit_url: str
    channel_id: str
    dev_secret: str

    @staticmethod
    def from_env() -> "AACPEnv":
        return AACPEnv(
            trust_url=os.getenv("AACP_TRUST_URL", "http://signature_trust_service:8000"),
            policy_url=os.getenv("AACP_POLICY_URL", "http://policy_plane_service:8000"),
            permit_url=os.getenv("AACP_PERMIT_URL", "http://permit_service:8000"),
            audit_url=os.getenv("AACP_AUDIT_URL", "http://audit_sink_service:8000"),
            channel_id=os.getenv("AACP_CHANNEL_ID", "channel::default"),
            dev_secret=os.getenv("AACP_DEV_SECRET", "change-me"),
        )

def build_headers(topic: str, producer_id: str, consumer_id: str, schema_id: str, schema_version: str, policy_id: str, policy_version: str, permit_id: str, intent_id: str) -> Dict[str, str]:
    trace_id = f"trc-{uuid.uuid4().hex}"
    event_id = f"evt-{uuid.uuid4().hex}"
    return {
        "x-aacp-trace-id": trace_id,
        "x-aacp-event-id": event_id,
        "x-aacp-producer-id": producer_id,
        "x-aacp-consumer-id": consumer_id,
        "x-aacp-channel-id": os.getenv("AACP_CHANNEL_ID", "channel::default"),
        "x-aacp-topic": topic,
        "x-aacp-schema-id": schema_id,
        "x-aacp-schema-version": schema_version,
        "x-aacp-policy-id": policy_id,
        "x-aacp-policy-version": policy_version,
        "x-aacp-permit-id": permit_id,
        "x-aacp-intent-id": intent_id,
        "x-aacp-sig-alg": "HMAC-SHA256-DEV",
        "x-aacp-signature": "TO_BE_SET",
    }

def sign_payload_dev(headers: Dict[str, str], payload: Dict[str, Any], dev_secret: str) -> Dict[str, str]:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    sig = _hmac_sha256_hex(dev_secret.encode("utf-8"), blob)
    headers = dict(headers)
    headers["x-aacp-signature"] = sig
    return headers

def make_interceptor(env: AACPEnv) -> AACKafkaInterceptor:
    endpoints = ServiceEndpoints(env.trust_url, env.policy_url, env.permit_url, env.audit_url)
    cfg = InterceptorConfig(endpoints=endpoints, channel_id_default=env.channel_id)
    return AACKafkaInterceptor(cfg)
