from __future__ import annotations
from typing import Dict, Any
import orjson
from .errors import ValidationError

class MessageCodec:
    """Strict encode/decode with schema_version presence. Fail-closed."""

    @staticmethod
    def encode(message: Dict[str, Any]) -> bytes:
        if "schema_version" not in message:
            raise ValidationError("schema_version is required")
        return orjson.dumps(message)

    @staticmethod
    def decode(raw: bytes) -> Dict[str, Any]:
        try:
            obj = orjson.loads(raw)
        except Exception as e:
            raise ValidationError(f"Invalid JSON payload: {e}") from e
        if not isinstance(obj, dict):
            raise ValidationError("Decoded payload must be an object")
        if "schema_version" not in obj:
            raise ValidationError("schema_version is required")
        return obj
