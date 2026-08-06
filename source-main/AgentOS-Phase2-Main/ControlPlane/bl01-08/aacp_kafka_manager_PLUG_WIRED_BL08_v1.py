# -*- coding: utf-8 -*-
"""
ARZIN / AACP - Plugin Manager (Wired) - BL-06/07/08
File: aacp_kafka_manager_PLUG_WIRED_BL08_v1.py

Purpose:
- Centralizes configuration for the interceptor wiring to:
  BL-06 Agent Registry, BL-07 Policy Plane, BL-08 Permit Service.
- Defaults are tight for hot path and Fail-Closed in phase 1.
"""
from __future__ import annotations

from dataclasses import dataclass
import os

from aacp_kafka_interceptor_PLUG_WIRED_BL08_v1 import AACPKafkaInterceptorWired, InterceptorSettings


@dataclass(frozen=True)
class WiredPluginConfig:
    registry_base_url: str = os.getenv("ARZIN_REGISTRY_URL", "http://agent-registry:8080")
    policy_base_url: str = os.getenv("ARZIN_POLICY_URL", "http://policy-plane:8081")
    permit_base_url: str = os.getenv("ARZIN_PERMIT_URL", "http://permit-service:8082")

    http_timeout_seconds: float = float(os.getenv("ARZIN_HTTP_TIMEOUT", "0.35"))
    cache_ttl_seconds: float = float(os.getenv("ARZIN_CACHE_TTL", "2.0"))
    cache_max_items: int = int(os.getenv("ARZIN_CACHE_MAX", "2048"))

    fail_closed: bool = os.getenv("ARZIN_FAIL_CLOSED", "true").lower() == "true"


def build_interceptor(cfg: WiredPluginConfig | None = None) -> AACPKafkaInterceptorWired:
    c = cfg or WiredPluginConfig()
    settings = InterceptorSettings(
        registry_base_url=c.registry_base_url,
        policy_base_url=c.policy_base_url,
        permit_base_url=c.permit_base_url,
        http_timeout_seconds=c.http_timeout_seconds,
        cache_ttl_seconds=c.cache_ttl_seconds,
        cache_max_items=c.cache_max_items,
        fail_closed=c.fail_closed,
    )
    return AACPKafkaInterceptorWired(settings=settings)
