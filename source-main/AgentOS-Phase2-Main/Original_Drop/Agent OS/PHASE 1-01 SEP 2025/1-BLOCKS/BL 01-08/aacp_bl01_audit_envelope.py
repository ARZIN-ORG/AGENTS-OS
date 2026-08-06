
# -*- coding: utf-8 -*-
"""
BL-01 — AACP Audit Envelope (Phase 1)

Non-negotiables (locked):
- Phase 1: no agent executes decisions (decision_class=execute is forbidden)
- Envelope is mandatory
- Deterministic chain hashing for tamper-evidence
- Fail-fast validation (no auto-fix, no silent coercions)

Notes:
- This is NOT an "audit log". This is the required envelope attached to each message.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator

_RFC3339_UTC_Z = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
_SHA256_HEX_64 = re.compile(r"^[a-f0-9]{64}$")
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json_bytes(obj: Any) -> bytes:
    # Deterministic across platforms.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def uuid7() -> str:
    """
    UUIDv7-ish generator without external deps.
    Good enough for Phase 1, monotonic at ms scale.
    """
    ts_ms = int(time.time() * 1000) & ((1 << 48) - 1)
    rnd = int.from_bytes(hashlib.sha256(str(time.time_ns()).encode("utf-8")).digest()[:10], "big") & ((1 << 74) - 1)
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


class EnvelopeVersion(str, Enum):
    v1_0 = "1.0"


class AgentClass(str, Enum):
    # Keep taxonomy minimal in Phase 1; expand later via registry metadata.
    security = "security"
    management = "management"
    integration = "integration"
    observe = "observe"


class DecisionClass(str, Enum):
    observe = "observe"
    recommend = "recommend"
    execute = "execute"


class SignatureAlg(str, Enum):
    Ed25519 = "Ed25519"
    ECDSA_P256 = "ECDSA-P256"
    RSA_PSS = "RSA-PSS"


class AACPAuditEnvelopeV1(BaseModel):
    envelope_version: EnvelopeVersion = Field(default=EnvelopeVersion.v1_0)

    message_id: str = Field(default_factory=uuid7)
    trace_id: str = Field(default_factory=uuid7)

    agent_id: str = Field(..., min_length=3, max_length=128)
    agent_class: AgentClass
    agent_version: str = Field(...)

    # Multi-channel must be explicit in every message.
    channel_id: str = Field(..., min_length=2, max_length=128)
    topic: str = Field(..., min_length=3, max_length=256)
    flow_id: str = Field(..., min_length=2, max_length=128)

    # Governance hooks (Phase 1: allow-list based)
    policy_id: str = Field(..., min_length=2, max_length=128)
    policy_version: str = Field(..., min_length=1, max_length=64)
    decision_class: DecisionClass

    event_time: str = Field(default_factory=utc_now_z)
    ingest_time: str = Field(default_factory=utc_now_z)

    # Security is mandatory. Verification is enforced by interceptor.
    signature: str = Field(..., min_length=16, max_length=8192)  # base64 recommended
    signature_alg: SignatureAlg
    key_id: str = Field(..., min_length=2, max_length=256)

    # Tamper-evidence chain.
    prev_chain_hash: Optional[str] = Field(default=None)
    chain_hash: str = Field(..., min_length=64, max_length=64)

    @validator("agent_version")
    def _semver(cls, v: str) -> str:
        if not _SEMVER.match(v):
            raise ValueError("agent_version must be semver (x.y.z)")
        return v

    @validator("event_time", "ingest_time")
    def _rfc3339z(cls, v: str) -> str:
        if not _RFC3339_UTC_Z.match(v):
            raise ValueError("timestamp must be RFC3339 UTC with Z suffix")
        return v

    @validator("decision_class")
    def _phase1_no_execute(cls, v: DecisionClass) -> DecisionClass:
        if v == DecisionClass.execute:
            raise ValueError("Phase 1 lock: decision_class=execute is forbidden")
        return v

    @validator("prev_chain_hash")
    def _prev_hash(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not _SHA256_HEX_64.fullmatch(v):
            raise ValueError("prev_chain_hash must be 64-char sha256 hex")
        return v

    @validator("chain_hash")
    def _chain_hash(cls, v: str) -> str:
        if not _SHA256_HEX_64.fullmatch(v):
            raise ValueError("chain_hash must be 64-char sha256 hex")
        return v


def envelope_without_chain(env: AACPAuditEnvelopeV1) -> Dict[str, Any]:
    d = env.dict()
    d.pop("chain_hash", None)
    return d


def compute_chain_hash(*, envelope_wo_chain: Dict[str, Any], payload: Dict[str, Any], prev_chain_hash: Optional[str]) -> str:
    blob = canonical_json_bytes(envelope_wo_chain) + b"|" + canonical_json_bytes(payload) + b"|"
    blob += (prev_chain_hash or "").encode("utf-8")
    return sha256_hex(blob)
