from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any
from .errors import ValidationError

# Phase-1 mandatory fields (10–15): strict
MANDATORY_FIELDS = [
    "trace_id",
    "message_id",
    "schema_version",
    "timestamp_ms",
    "producer_id",
    "consumer_id",
    "channel",
    "policy_scope",
    "signature_alg",
    "signature",
    "chain_hash",
    "permit_status",
    "audit_version",
]

@dataclass(frozen=True)
class AuditEnvelope:
    trace_id: str
    message_id: str
    schema_version: str
    timestamp_ms: int
    producer_id: str
    consumer_id: str
    channel: str
    policy_scope: str
    signature_alg: str
    signature: str
    chain_hash: str
    permit_status: str
    audit_version: str
    extra: Optional[Dict[str, Any]] = None

class AuditEnvelopeBuilder:
    @staticmethod
    def build(payload: Dict[str, Any]) -> AuditEnvelope:
        missing = [k for k in MANDATORY_FIELDS if k not in payload or payload[k] in (None, "", [])]
        if missing:
            raise ValidationError(f"Missing mandatory audit fields: {missing}")

        return AuditEnvelope(
            trace_id=str(payload["trace_id"]),
            message_id=str(payload["message_id"]),
            schema_version=str(payload["schema_version"]),
            timestamp_ms=int(payload["timestamp_ms"]),
            producer_id=str(payload["producer_id"]),
            consumer_id=str(payload["consumer_id"]),
            channel=str(payload["channel"]),
            policy_scope=str(payload["policy_scope"]),
            signature_alg=str(payload["signature_alg"]),
            signature=str(payload["signature"]),
            chain_hash=str(payload["chain_hash"]),
            permit_status=str(payload["permit_status"]),
            audit_version=str(payload["audit_version"]),
            extra={k:v for k,v in payload.items() if k not in MANDATORY_FIELDS},
        )
