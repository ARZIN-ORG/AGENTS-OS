from __future__ import annotations
from .types import PolicyScope, ChannelBinding
from .errors import ScopeError

def assert_scope_bound(scope: PolicyScope) -> None:
    if not scope.value or scope.value.strip() == "":
        raise ScopeError("policy scope must be explicitly set (no implicit scope)")

def assert_channel_bound(binding: ChannelBinding) -> None:
    t = (binding.topic or "").strip()
    if not t or "*" in t or "#" in t:
        raise ScopeError("channel topic must be explicit; wildcards are forbidden by default")
