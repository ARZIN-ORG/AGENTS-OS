# Recommendation / Suggestion Agent - Domain Layer (Mandatory)
# Output: Recommendations only. Must NOT publish operational actions directly.
# Enforced: always returns a 'requires_human_approval' flag.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class Suggestion:
    suggestion_id: str
    title: str
    rationale: str
    suggested_next_steps: List[str]
    requires_human_approval: bool
    confidence: float
    evidence: Dict[str, Any]


class RecommendationSuggestionAgent:
    def suggest(self, context: Dict[str, Any]) -> List[Suggestion]:
        if not context:
            return []

        # Deterministic suggestions based on explicit signals.
        suggestions: List[Suggestion] = []

        if context.get("dlq_growth_rate", 0) > 0:
            suggestions.append(
                Suggestion(
                    suggestion_id="SUG-001",
                    title="DLQ growth observed: prioritize triage",
                    rationale="DLQ growth indicates systemic reject/retry pressure; triage reduces hidden backlog risk.",
                    suggested_next_steps=[
                        "Inspect DLQ topics and top reject reasons",
                        "Validate schema/version mismatches",
                        "Consider temporary throttling with human approval",
                    ],
                    requires_human_approval=True,
                    confidence=0.76,
                    evidence={"dlq_growth_rate": context.get("dlq_growth_rate")},
                )
            )

        if not suggestions:
            suggestions.append(
                Suggestion(
                    suggestion_id="SUG-BASELINE",
                    title="No urgent recommendation",
                    rationale="No explicit risk indicators were provided above threshold.",
                    suggested_next_steps=["Continue monitoring", "Request richer context if needed"],
                    requires_human_approval=False,
                    confidence=0.55,
                    evidence={"context_keys": sorted(list(context.keys()))},
                )
            )

        return suggestions
