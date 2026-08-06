"""SOHA hook adapter — wraps AACP interceptor.

This is designed to be called from SOHA API Flow Manager or gateway hooks.
It enforces the same gate: signature->policy->permit->audit before publish.
"""

from __future__ import annotations
from typing import Any, Dict, Tuple
from libs.aacp_kafka.kafka_io import AACPEnv, make_interceptor

class SohaKafkaHookAdapter:
    def __init__(self):
        self._env = AACPEnv.from_env()
        self._interceptor = make_interceptor(self._env)

    def before_publish(self, headers: Dict[str, str], payload: Dict[str, Any], human_approved: bool) -> Tuple[Dict[str, str], Dict[str, Any]]:
        return self._interceptor.guard_publish(headers=headers, payload=payload, human_approved=human_approved)

    def after_consume(self, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        return self._interceptor.guard_consume(headers=headers, payload=payload)
