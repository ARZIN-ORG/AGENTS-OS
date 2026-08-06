from __future__ import annotations
from typing import Protocol, Optional
import hmac
import hashlib

class KeyStore(Protocol):
    def get_key(self, key_id: str) -> bytes:
        ...

class FileKeyStore:
    """Dev keystore (replace with HSM/KMS in production)."""
    def __init__(self, secret: bytes):
        self._secret = secret

    def get_key(self, key_id: str) -> bytes:
        return self._secret

def verify_hmac_sha256(keystore: KeyStore, key_id: str, message: bytes, signature_hex: str) -> bool:
    key = keystore.get_key(key_id)
    sig = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, signature_hex)
