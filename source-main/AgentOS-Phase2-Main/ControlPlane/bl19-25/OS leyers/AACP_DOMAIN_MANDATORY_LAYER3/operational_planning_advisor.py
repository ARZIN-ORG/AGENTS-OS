# Operational Planning Advisor - Domain Layer (Mandatory)
# Output: Scenarios + trade-offs only. No autonomous decisions/execution.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Constraint:
    key: str
    value: Any
    rationale: str


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    title: str
    expected_benefit: str
    expected_risk: str
    operational_steps: List[str]
    assumptions: List[str]
    constraints: List[Constraint]
    confidence: float  # 0..1


class OperationalPlanningAdvisor:
    def propose(self, context: Dict[str, Any], constraints: List[Constraint]) -> List[Scenario]:
        # Fail-closed: if no context, return no scenario rather than hallucinate.
        if not context:
            return []

        # Minimal scenario framework: deterministic + auditable.
        # Real implementations can plug into optimization/forecast engines, but must remain advisory.
        base_assumptions = [
            "Human approval required for any action",
            "Permit service gate is enforced",
            "AACP channels are used for any publish",
        ]

        s1 = Scenario(
            scenario_id="SCN-OPS-001",
            title="Conservative stabilization plan",
            expected_benefit="Reduce operational volatility by prioritizing stability over throughput.",
            expected_risk="May reduce short-term throughput/headroom.",
            operational_steps=[
                "Throttle non-critical workloads via approved change",
                "Increase monitoring granularity for hotspot components",
                "Schedule maintenance windows for high-risk components",
            ],
            assumptions=base_assumptions,
            constraints=constraints,
            confidence=0.72,
        )

        s2 = Scenario(
            scenario_id="SCN-OPS-002",
            title="Balanced performance plan",
            expected_benefit="Maintain throughput while addressing top-risk bottlenecks.",
            expected_risk="Residual risk remains for low-visibility failure modes.",
            operational_steps=[
                "Targeted scaling for bottleneck services (stateless first)",
                "Introduce backpressure thresholds on busy topics",
                "Validate DLQ growth and adjust retry policy",
            ],
            assumptions=base_assumptions,
            constraints=constraints,
            confidence=0.66,
        )

        return [s1, s2]
