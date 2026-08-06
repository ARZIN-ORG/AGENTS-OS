
# -*- coding: utf-8 -*-
"""
BL-03 — KeyStore + Signature Verification (Phase 1)

Locked behavior:
- Signature verification is mandatory.
- Unknown key_id => verification fails.
- Deterministic signing bytes (canonical JSON).
- No network calls in this module. HSM integration is done via KeyStore adapter.

Assumptions:
- envelope.signature is base64 of raw signature bytes.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, ec, padding, rsa

from aacp_bl01_audit_envelope import AACPAuditEnvelopeV1, SignatureAlg

def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def signing_bytes(envelope: AACPAuditEnvelopeV1, payload: Dict[str, Any]) -> bytes:
    # Sign envelope minus signature field.
    env = envelope.dict()
    env.pop("signature", None)
    return canonical_json_bytes(env) + b"|" + canonical_json_bytes(payload)

class KeyStore(Protocol):
    def get_public_key_pem(self, key_id: str) -> Optional[str]:
        ...

@dataclass(frozen=True)
class InMemoryKeyStore(KeyStore):
    keys: Dict[str, str]
    def get_public_key_pem(self, key_id: str) -> Optional[str]:
        return self.keys.get(key_id)

@dataclass(frozen=True)
class FileKeyStore(KeyStore):
    keys: Dict[str, str]

    @classmethod
    def from_json_file(cls, path: str) -> "FileKeyStore":
        import json as _json
        with open(path, "r", encoding="utf-8") as f:
            data = _json.load(f)
        if not isinstance(data, dict) or "keys" not in data or not isinstance(data["keys"], dict):
            raise ValueError("invalid keystore json; expected {'keys': {key_id: pem, ...}}")
        keys: Dict[str, str] = {}
        for k, v in data["keys"].items():
            if not isinstance(k, str) or not isinstance(v, str):
                raise ValueError("invalid keystore entry; key_id and pem must be strings")
            keys[k] = v
        return cls(keys=keys)

    def get_public_key_pem(self, key_id: str) -> Optional[str]:
        return self.keys.get(key_id)

def _load_public_key(pem: str):
    return serialization.load_pem_public_key(pem.encode("utf-8"))

def verify_signature(*, envelope: AACPAuditEnvelopeV1, payload: Dict[str, Any], keystore: KeyStore) -> bool:
    pem = keystore.get_public_key_pem(envelope.key_id)
    if not pem:
        return False

    data = signing_bytes(envelope, payload)

    try:
        sig = base64.b64decode(envelope.signature.encode("utf-8"), validate=True)
    except Exception:
        return False

    pub = _load_public_key(pem)

    try:
        if envelope.signature_alg == SignatureAlg.Ed25519:
            if not isinstance(pub, ed25519.Ed25519PublicKey):
                return False
            pub.verify(sig, data)
            return True

        if envelope.signature_alg == SignatureAlg.ECDSA_P256:
            if not isinstance(pub, ec.EllipticCurvePublicKey):
                return False
            pub.verify(sig, data, ec.ECDSA(hashes.SHA256()))
            return True

        if envelope.signature_alg == SignatureAlg.RSA_PSS:
            if not isinstance(pub, rsa.RSAPublicKey):
                return False
            pub.verify(
                sig,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True

        return False

    except InvalidSignature:
        return False
    except Exception:
        return False
