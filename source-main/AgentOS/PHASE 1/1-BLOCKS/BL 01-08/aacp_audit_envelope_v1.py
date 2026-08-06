# aacp_audit_envelope_v1.py
# -*- coding: utf-8 -*-
"""
AACP Audit Envelope v1 (BL-01)
Hard validation. No auto-fix. Deterministic chain hashing.
"""

from __future__ import annotations

import json
import re
import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


RFC3339_UTC_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def uuid7() -> str:
    ts_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    rnd = int.from_bytes(hashlib.sha256(str(time.time_ns()).encode("utf-8")).digest()[:10], "big")
    rnd &= ((1 << 74) - 1)
    ver = 0x7
    var = 0x2
    rand_a = (rnd >> 62) & ((1 << 12) - 1)
    rand_b = rnd & ((1 << 62) - 1)
    uuid_int = (ts_ms << 80)
    uuid_int |= (ver << 76)
    uuid_int |= (rand_a << 64)
    uuid_int |= (var << 62)
    uuid_int |= rand_b
    hex32 = f"{uuid_int:032x}"
    return f"{hex32[0:8]}-{hex32[8:12]}-{hex32[12:16]}-{hex32[16:20]}-{hex32[20:32]}"


class AgentType(str, Enum):
    security = "security"
    management = "management"
    integration = "integration"
    observe = "observe"


class DecisionClass(str, Enum):
    observe = "observe"
    recommend = "recommend"
    execute = "execute"


class EnvelopeVersion(str, Enum):
    v1_0 = "1.0"


class SignatureAlg(str, Enum):
    Ed25519 = "Ed25519"
    ECDSA_P256 = "ECDSA-P256"
    RSA_PSS = "RSA-PSS"


class AACPAuditEnvelopeV1(BaseModel):
    envelope_version: EnvelopeVersion = Field(default=EnvelopeVersion.v1_0)

    message_id: str = Field(default_factory=uuid7)
    trace_id: str = Field(default_factory=uuid7)
    agent_id: str = Field(..., min_length=3, max_length=128)
    agent_type: AgentType
    agent_version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")

    channel_id: str = Field(..., min_length=3, max_length=128)
    topic: str = Field(..., min_length=3, max_length=256)
    flow_id: str = Field(..., min_length=3, max_length=128)

    policy_id: str = Field(..., min_length=3, max_length=128)
    policy_version: str = Field(..., min_length=1, max_length=64)
    decision_class: DecisionClass

    event_time: str = Field(default_factory=utc_now_z)
    ingest_time: str = Field(default_factory=utc_now_z)

    signature: str = Field(..., min_length=16, max_length=8192)
    signature_alg: SignatureAlg
    key_id: str = Field(..., min_length=3, max_length=256)

    prev_chain_hash: Optional[str] = Field(default=None)
    chain_hash: str = Field(..., min_length=64, max_length=64)

    @validator("event_time", "ingest_time")
    def _validate_rfc3339_z(cls, v: str) -> str:
        if not RFC3339_UTC_Z_RE.match(v):
            raise ValueError("timestamp must be RFC3339 UTC with Z suffix")
        return v

    @validator("decision_class")
    def _phase1_forbid_execute(cls, v: DecisionClass) -> DecisionClass:
        if v == DecisionClass.execute:
            raise ValueError("Phase 1: decision_class=execute is forbidden")
        return v

    @validator("prev_chain_hash")
    def _validate_prev_hash(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r"^[a-f0-9]{64}$", v):
            raise ValueError("prev_chain_hash must be 64-char hex sha256")
        return v

    @validator("chain_hash")
    def _validate_chain_hash(cls, v: str) -> str:
        if not re.fullmatch(r"^[a-f0-9]{64}$", v):
            raise ValueError("chain_hash must be 64-char hex sha256")
        return v


def compute_chain_hash(*, envelope_without_chain: Dict[str, Any], payload: Dict[str, Any], prev_chain_hash: Optional[str]) -> str:
    blob = _canonical_json(envelope_without_chain) + b"|" + _canonical_json(payload) + b"|"
    blob += (prev_chain_hash or "").encode("utf-8")
    return sha256_hex(blob)


@dataclass(frozen=True)
class EnvelopeValidationResult:
    ok: bool
    reason_code: Optional[str] = None
    reason: Optional[str] = None
