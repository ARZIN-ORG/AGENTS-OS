# aacp_signature_verifier.py
# -*- coding: utf-8 -*-
"""
Signature Verifier (Phase 1)
- Deterministic signing bytes
- Keystore-backed public key lookup (HSM/KeyStore abstraction)
- Strict: unknown key_id => verify=False

This module is intentionally small and explicit.
No network calls. No magic.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, ec, padding, rsa

from aacp_audit_envelope_v1 import AACPAuditEnvelopeV1, SignatureAlg


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def signing_bytes(envelope: AACPAuditEnvelopeV1, payload: Dict[str, Any]) -> bytes:
    """
    Deterministic signing bytes for Phase 1.

    We sign:
      canonical(envelope_without_signature) + "|" + canonical(payload)

    Notes:
    - We do NOT include "signature" itself.
    - We keep chain_hash included (tamper-evidence) because it's already deterministic.
    """
    env = envelope.dict()
    env.pop("signature", None)
    blob = canonical_json_bytes(env) + b"|" + canonical_json_bytes(payload)
    return blob


class KeyStore(Protocol):
    def get_public_key_pem(self, key_id: str) -> Optional[str]:
        ...


@dataclass
class InMemoryKeyStore(KeyStore):
    """
    Minimal KeyStore for Phase 1 / tests.
    Maps key_id -> PEM public key string.
    """
    keys: Dict[str, str]

    def get_public_key_pem(self, key_id: str) -> Optional[str]:
        return self.keys.get(key_id)


def _load_public_key(pem: str):
    return serialization.load_pem_public_key(pem.encode("utf-8"))


def verify_signature(
    *,
    envelope: AACPAuditEnvelopeV1,
    payload: Dict[str, Any],
    keystore: KeyStore,
) -> bool:
    pem = keystore.get_public_key_pem(envelope.key_id)
    if not pem:
        return False

    data = signing_bytes(envelope, payload)

    # Expect signature as base64 (standard). If it's hex or raw, verification will fail.
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
