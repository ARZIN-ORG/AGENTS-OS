
# -*- coding: utf-8 -*-
"""
BL-04 — Agent Registry + Policy Resolver (Phase 1 Minimal)

Locked behavior:
- Allow-list only. Unknown => reject.
- Policy is versioned.
- Channel/topic constraints are enforced here (control plane).
- Phase 1: decision_class=execute forbidden (also enforced by BL-01).

This module provides in-memory implementations and file loaders for Private Cloud.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Optional, Protocol, Set

from aacp_bl01_audit_envelope import DecisionClass

class AgentRegistryLike(Protocol):
    def is_registered(self, agent_id: str) -> bool:
        ...
    def allowed_channels(self, agent_id: str) -> Set[str]:
        ...
    def allowed_topics(self, agent_id: str) -> Set[str]:
        ...

class PolicyResolverLike(Protocol):
    def is_policy_active(self, policy_id: str, policy_version: str) -> bool:
        ...
    def allowed_decision_classes(self, policy_id: str, policy_version: str) -> Set[str]:
        ...
    def allowed_channels(self, policy_id: str, policy_version: str) -> Set[str]:
        ...
    def allowed_topics(self, policy_id: str, policy_version: str) -> Set[str]:

        ...

@dataclass(frozen=True)
class InMemoryAgentRegistry(AgentRegistryLike):
    agents: Dict[str, dict]

    def is_registered(self, agent_id: str) -> bool:
        return agent_id in self.agents

    def allowed_channels(self, agent_id: str) -> Set[str]:
        meta = self.agents.get(agent_id, {})
        return set(meta.get("channels", []))

    def allowed_topics(self, agent_id: str) -> Set[str]:
        meta = self.agents.get(agent_id, {})
        return set(meta.get("topics", []))

@dataclass(frozen=True)
class InMemoryPolicyResolver(PolicyResolverLike):
    policies: Dict[str, Dict[str, dict]]
    # policies[policy_id][policy_version] = {"active": bool, "decision_classes":[...], "channels":[...], "topics":[...]}

    def is_policy_active(self, policy_id: str, policy_version: str) -> bool:
        return policy_id in self.policies and policy_version in self.policies[policy_id] and bool(self.policies[policy_id][policy_version].get("active", False))

    def allowed_decision_classes(self, policy_id: str, policy_version: str) -> Set[str]:
        meta = self.policies.get(policy_id, {}).get(policy_version, {})
        classes = set(meta.get("decision_classes", []))
        # Phase 1 hard lock (belt + suspenders)
        classes.discard(DecisionClass.execute.value)
        return classes

    def allowed_channels(self, policy_id: str, policy_version: str) -> Set[str]:
        meta = self.policies.get(policy_id, {}).get(policy_version, {})
        return set(meta.get("channels", []))

    def allowed_topics(self, policy_id: str, policy_version: str) -> Set[str]:
        meta = self.policies.get(policy_id, {}).get(policy_version, {})
        return set(meta.get("topics", []))

def load_registry_from_json(path: str) -> InMemoryAgentRegistry:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "agents" not in data or not isinstance(data["agents"], dict):
        raise ValueError("invalid registry json; expected {'agents': {...}}")
    return InMemoryAgentRegistry(agents=data["agents"])

def load_policies_from_json(path: str) -> InMemoryPolicyResolver:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "policies" not in data or not isinstance(data["policies"], dict):
        raise ValueError("invalid policies json; expected {'policies': {...}}")
    return InMemoryPolicyResolver(policies=data["policies"])
