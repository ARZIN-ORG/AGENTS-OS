from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from .errors import SecurityError, ValidationError

@dataclass(frozen=True)
class SignatureVerifier:
    """Verify signatures. No signing helper exposed to partners by default."""
    public_cert_pem: bytes

    def verify(self, message_bytes: bytes, signature: bytes) -> bool:
        if not self.public_cert_pem:
            raise ValidationError("public_cert_pem is required")
        try:
            cert = load_pem_x509_certificate(self.public_cert_pem)
            pub = cert.public_key()
            pub.verify(
                signature,
                message_bytes,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception as e:
            raise SecurityError(f"Signature verification failed: {e}") from e
