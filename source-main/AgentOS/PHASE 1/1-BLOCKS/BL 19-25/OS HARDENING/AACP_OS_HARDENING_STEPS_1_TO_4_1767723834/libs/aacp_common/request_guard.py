from __future__ import annotations

from fastapi import Header
from typing import Optional
from .errors import RejectError
from .locked import LOCKS

# Minimal request contract for OS-Native microservices.
REQUIRED_HEADERS = [
    "x-aacp-trace-id",
    "x-aacp-event-id",
    "x-aacp-producer-id",
    "x-aacp-consumer-id",
    "x-aacp-channel-id",
    "x-aacp-topic",
    "x-aacp-schema-id",
    "x-aacp-schema-version",
    "x-aacp-policy-id",
    "x-aacp-policy-version",
    "x-aacp-permit-id",
    "x-aacp-intent-id",
    "x-aacp-sig-alg",
    "x-aacp-signature",
]

def enforce_locked_constraints():
    if not LOCKS.get("no_autonomous_decisions", False):
        raise RejectError("LOCK_BROKEN", "no_autonomous_decisions lock must remain true")

def require_aacp_headers(**headers):
    missing = [h for h in REQUIRED_HEADERS if not headers.get(h)]
    if missing:
        raise RejectError("MISSING_HEADERS", f"Missing required AACP headers: {missing}")

def aacp_guard(
    x_aacp_trace_id: str = Header(..., alias="x-aacp-trace-id"),
    x_aacp_event_id: str = Header(..., alias="x-aacp-event-id"),
    x_aacp_producer_id: str = Header(..., alias="x-aacp-producer-id"),
    x_aacp_consumer_id: str = Header(..., alias="x-aacp-consumer-id"),
    x_aacp_channel_id: str = Header(..., alias="x-aacp-channel-id"),
    x_aacp_topic: str = Header(..., alias="x-aacp-topic"),
    x_aacp_schema_id: str = Header(..., alias="x-aacp-schema-id"),
    x_aacp_schema_version: str = Header(..., alias="x-aacp-schema-version"),
    x_aacp_policy_id: str = Header(..., alias="x-aacp-policy-id"),
    x_aacp_policy_version: str = Header(..., alias="x-aacp-policy-version"),
    x_aacp_permit_id: str = Header(..., alias="x-aacp-permit-id"),
    x_aacp_intent_id: str = Header(..., alias="x-aacp-intent-id"),
    x_aacp_sig_alg: str = Header(..., alias="x-aacp-sig-alg"),
    x_aacp_signature: str = Header(..., alias="x-aacp-signature"),
):
    enforce_locked_constraints()
    return {
        "trace_id": x_aacp_trace_id,
        "event_id": x_aacp_event_id,
        "producer_id": x_aacp_producer_id,
        "consumer_id": x_aacp_consumer_id,
        "channel_id": x_aacp_channel_id,
        "topic": x_aacp_topic,
        "schema_id": x_aacp_schema_id,
        "schema_version": x_aacp_schema_version,
        "policy_id": x_aacp_policy_id,
        "policy_version": x_aacp_policy_version,
        "permit_id": x_aacp_permit_id,
        "intent_id": x_aacp_intent_id,
        "sig_alg": x_aacp_sig_alg,
        "signature": x_aacp_signature,
    }
