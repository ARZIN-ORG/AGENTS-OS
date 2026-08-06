from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
from .codec import MessageCodec
from .audit import AuditEnvelopeBuilder
from .types import PolicyScope, ChannelBinding
from .guardrails import assert_scope_bound, assert_channel_bound

@dataclass
class ShadowClient:
    """Shadow client used for sandbox testing. NO side-effects by design."""
    scope: PolicyScope
    channel: ChannelBinding

    def prepare(self, raw_message: Dict[str, Any]) -> Dict[str, Any]:
        assert_scope_bound(self.scope)
        assert_channel_bound(self.channel)

        # Enforce audit envelope presence and validity
        audit = raw_message.get("audit", None)
        if not isinstance(audit, dict):
            raise ValueError("audit envelope is required as object")
        AuditEnvelopeBuilder.build(audit)

        # Tag as SHADOW; never allow EXECUTE intent
        raw_message.setdefault("mode", "SHADOW")
        raw_message["mode"] = "SHADOW"
        raw_message.setdefault("intent", "RECOMMENDATION")
        if raw_message.get("intent") == "EXECUTE":
            raise ValueError("EXECUTE intent is forbidden in partner SDK")

        return raw_message

    def encode(self, msg: Dict[str, Any]) -> bytes:
        return MessageCodec.encode(msg)

    def decode(self, raw: bytes) -> Dict[str, Any]:
        return MessageCodec.decode(raw)
