# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List


class ValidationError(ValueError):
    pass


def normalize_scope_key(scope: Dict[str, Any]) -> str:
    agent_class = str(scope.get("agent_class", "")).strip()
    agent_id = str(scope.get("agent_id") or "").strip()
    channel_id = str(scope.get("channel_id", "")).strip()
    return f"{agent_class}::{agent_id}::{channel_id}"


def validate_phase1_policy(scope: Dict[str, Any], constraints: Dict[str, Any]) -> None:
    # Scope basics
    if not scope.get("agent_class"):
        raise ValidationError("scope.agent_class_required")
    if not scope.get("channel_id"):
        raise ValidationError("scope.channel_id_required")
    topics = scope.get("topics") or []
    if not topics:
        raise ValidationError("scope.topics_required")
    for t in topics:
        if not t.get("topic"):
            raise ValidationError("scope.topic_required")
        pattern = t.get("pattern", "literal")
        if pattern not in ("literal", "prefix"):
            raise ValidationError("scope.topic_pattern_invalid")

    # Constraints: Phase1 only observe/recommend
    dcs = constraints.get("decision_classes") or []
    allowed = {"observe", "recommend"}
    if not dcs:
        raise ValidationError("constraints.decision_classes_required")
    for dc in dcs:
        if dc not in allowed:
            raise ValidationError(f"constraints.decision_class_not_allowed_in_phase1:{dc}")

    # Signature required default: true (fail closed)
    sig_req = constraints.get("signature_required")
    if sig_req is None:
        raise ValidationError("constraints.signature_required_required")
    if sig_req is not True:
        # For phase1 we fail closed.
        raise ValidationError("constraints.signature_required_must_be_true_in_phase1")

    # TTL bounds sanity
    ttl_min = int(constraints.get("ttl_seconds_min", 1))
    ttl_max = int(constraints.get("ttl_seconds_max", 300))
    if ttl_min < 1 or ttl_max < ttl_min:
        raise ValidationError("constraints.ttl_bounds_invalid")

    max_payload = int(constraints.get("max_payload_bytes", 1048576))
    if max_payload < 1024:
        raise ValidationError("constraints.max_payload_bytes_too_small")
