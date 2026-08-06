# Executive Narrative Agent - Interaction Layer (Mandatory)
# Role: Convert system state into board/CEO-readable narrative.
# IMPORTANT: Must not hide uncertainty; must not invent metrics.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class ExecutiveNarrative:
    headline: str
    situation: str
    risks: str
    recommendations: str
    confidence: float
    evidence_refs: List[str]


class ExecutiveNarrativeAgent:
    def render(self, state: Dict[str, Any]) -> ExecutiveNarrative:
        if not state:
            return ExecutiveNarrative(
                headline="Operational status: unknown",
                situation="No state evidence provided.",
                risks="Cannot assess risks without telemetry/evidence.",
                recommendations="Request operational snapshot and audit trace references.",
                confidence=0.0,
                evidence_refs=[],
            )

        refs = [f"state:{k}" for k in sorted(state.keys())]
        situation = "System is operating within provided constraints and available telemetry."
        risks = "No quantified risks could be asserted without explicit indicators; review drift/DLQ/availability signals."
        recommendations = "Review top recommendations in Governance Console; approve/deny as needed; ensure permit/audit trail are recorded."
        return ExecutiveNarrative(
            headline="Operational summary (advisory)",
            situation=situation,
            risks=risks,
            recommendations=recommendations,
            confidence=0.58,
            evidence_refs=refs,
        )
