# aacp_registry_policy_min.py
# -*- coding: utf-8 -*-
"""
Agent Registry + Policy Resolver (Phase 1 - Minimal)

Strict behavior:
- registry/policy are allow-lists
- unknown => False
- no auto-enroll
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Dict, Protocol


class AgentRegistryLike(Protocol):
    def is_registered(self, agent_id: str) -> bool:
        ...


class PolicyResolverLike(Protocol):
    def is_policy_active(self, policy_id: str, policy_version: str) -> bool:
        ...


@dataclass
class InMemoryAgentRegistry(AgentRegistryLike):
    agents: Dict[str, dict]

    def is_registered(self, agent_id: str) -> bool:
        return agent_id in self.agents


@dataclass
class InMemoryPolicyResolver(PolicyResolverLike):
    policies: Dict[str, Dict[str, dict]]
    # policies[policy_id][policy_version] = {...}

    def is_policy_active(self, policy_id: str, policy_version: str) -> bool:
        return policy_id in self.policies and policy_version in self.policies[policy_id]


def load_registry_from_json(path: str) -> InMemoryAgentRegistry:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "agents" not in data:
        raise ValueError("invalid registry json; expected {'agents': {...}}")
    return InMemoryAgentRegistry(agents=data["agents"])


def load_policies_from_json(path: str) -> InMemoryPolicyResolver:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or "policies" not in data:
        raise ValueError("invalid policies json; expected {'policies': {...}}")
    return InMemoryPolicyResolver(policies=data["policies"])
