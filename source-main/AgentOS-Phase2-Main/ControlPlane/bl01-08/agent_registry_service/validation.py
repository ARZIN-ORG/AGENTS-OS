# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .models import AgentClass, DecisionClass


class ValidationError(ValueError):
    pass


def validate_phase1_constraints(agent_class: AgentClass, decision_classes: List[str], channels: List[Dict[str, Any]]) -> None:
    # Phase 1 hard rule: no execution decisions. Only observe/recommend are allowed.
    allowed = {DecisionClass.observe.value, DecisionClass.recommend.value}
    for dc in decision_classes:
        if dc not in allowed:
            raise ValidationError(f"decision_class_not_allowed_in_phase1: {dc}")

    # Phase 1: execution agents exist as "hands" but still must not declare execute.
    # We allow 'execution' class to exist for later phases, but phase1 decision_classes remain constrained.

    # Channels must be explicit, non-empty, and with at least one topic rule each.
    if not channels:
        raise ValidationError("channels_required")
    for ch in channels:
        if "channel_id" not in ch or not str(ch["channel_id"]).strip():
            raise ValidationError("channel_id_required")
        topics = ch.get("topics") or []
        if not topics:
            raise ValidationError("topics_required_per_channel")
        for t in topics:
            topic = t.get("topic")
            if not topic or not str(topic).strip():
                raise ValidationError("topic_required")
            pattern = t.get("pattern", "literal")
            if pattern not in ("literal", "prefix"):
                raise ValidationError(f"invalid_topic_pattern: {pattern}")
