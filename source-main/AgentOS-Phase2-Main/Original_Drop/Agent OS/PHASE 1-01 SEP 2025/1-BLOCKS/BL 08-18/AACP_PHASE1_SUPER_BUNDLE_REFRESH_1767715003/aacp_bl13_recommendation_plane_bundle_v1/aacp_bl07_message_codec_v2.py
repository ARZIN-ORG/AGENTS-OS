
# -*- coding: utf-8 -*-
"""
BL-07 — Message Codec (Phase 1)

Purpose:
- Canonical serialization for transport.
- Optional payload hashing for quick integrity checks.
- Minimal allocations: dict -> bytes once.

Notes:
- This codec does not do encryption. Encryption is envelope-level/transport-level.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

@dataclass(frozen=True)
class EncodedMessage:
    value: bytes
    payload_hash: str

def encode_message(message_dict: Dict[str, Any]) -> EncodedMessage:
    b = canonical_json_bytes(message_dict)
    return EncodedMessage(value=b, payload_hash=sha256_hex(b))
def build_suggestion_event(
    suggestion_id: str,
    event_type: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    """Build a non-operational suggestion event dict.

    Output is meant to be wrapped by BL-01 Audit Envelope.
    No publish / no execute / no authority.
    """
    return {
        "kind": "SUGGESTION_EVENT",
        "suggestion_id": suggestion_id,
        "event_type": event_type,
        "payload": payload,
    }

