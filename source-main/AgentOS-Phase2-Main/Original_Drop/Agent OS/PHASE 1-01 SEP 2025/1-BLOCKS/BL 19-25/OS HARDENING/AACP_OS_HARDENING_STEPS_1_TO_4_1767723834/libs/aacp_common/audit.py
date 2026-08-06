from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import time
import hashlib
import json

REQUIRED_AUDIT_FIELDS = [
    "trace_id",
    "event_id",
    "timestamp_ms",
    "producer_id",
    "consumer_id",
    "channel_id",
    "topic",
    "schema_id",
    "schema_version",
    "policy_id",
    "policy_version",
    "permit_id",
    "intent_id",
    "sig_alg",
    "signature",
]

class AuditEnvelope(BaseModel):
    trace_id: str = Field(..., min_length=8, max_length=128)
    event_id: str = Field(..., min_length=8, max_length=128)
    timestamp_ms: int = Field(default_factory=lambda: int(time.time() * 1000))

    producer_id: str = Field(..., min_length=3, max_length=128)
    consumer_id: str = Field(..., min_length=3, max_length=128)

    channel_id: str = Field(..., min_length=3, max_length=128)
    topic: str = Field(..., min_length=1, max_length=256)

    schema_id: str = Field(..., min_length=3, max_length=128)
    schema_version: str = Field(..., min_length=1, max_length=32)

    policy_id: str = Field(..., min_length=3, max_length=128)
    policy_version: str = Field(..., min_length=1, max_length=64)

    permit_id: str = Field(..., min_length=3, max_length=128)
    intent_id: str = Field(..., min_length=3, max_length=128)

    sig_alg: str = Field(..., min_length=3, max_length=64)
    signature: str = Field(..., min_length=8, max_length=4096)

    chain_hash: Optional[str] = Field(default=None, min_length=16, max_length=128)

    extras: Dict[str, Any] = Field(default_factory=dict)

    def compute_chain_hash(self, prev_hash: Optional[str]) -> str:
        payload = self.model_dump()
        payload["prev_hash"] = prev_hash or ""
        blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

def require_fields(d: dict) -> List[str]:
    missing = []
    for f in REQUIRED_AUDIT_FIELDS:
        if f not in d or d[f] in (None, "", []):
            missing.append(f)
    return missing
