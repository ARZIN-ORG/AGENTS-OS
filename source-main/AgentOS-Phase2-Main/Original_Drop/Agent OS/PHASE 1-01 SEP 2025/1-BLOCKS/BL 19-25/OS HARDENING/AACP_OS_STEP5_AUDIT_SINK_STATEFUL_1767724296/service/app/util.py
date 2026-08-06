from __future__ import annotations
from typing import Any, Dict, Optional
import hashlib
import json
import time
import uuid

def now_ms() -> int:
    return int(time.time() * 1000)

def new_id(prefix: str = "aud") -> str:
    return f"{prefix}-{uuid.uuid4().hex}"

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_chain_hash(prev_chain_hash: Optional[str], envelope: Dict[str, Any], payload_digest: Optional[str], seq: int) -> str:
    prev = (prev_chain_hash or "").encode("utf-8")
    env = canonical_json_bytes(envelope)
    dig = (payload_digest or "").encode("utf-8")
    seq_b = str(seq).encode("utf-8")
    return sha256_hex(prev + b"|" + env + b"|" + dig + b"|" + seq_b)
