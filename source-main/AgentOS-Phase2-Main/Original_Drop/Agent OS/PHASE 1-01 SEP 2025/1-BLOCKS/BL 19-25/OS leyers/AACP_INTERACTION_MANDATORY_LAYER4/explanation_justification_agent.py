# Explanation & Justification Agent - Interaction Layer (Mandatory)
# Role: Explain why a recommendation/permit decision was suggested.
# IMPORTANT: No decisions. Only narrative grounded in provided evidence.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Explanation:
    title: str
    summary: str
    evidence_refs: List[str]
    limitations: List[str]


class ExplanationJustificationAgent:
    def explain(self, topic: str, evidence: Dict[str, Any]) -> Explanation:
        if not evidence:
            return Explanation(
                title=f"Explanation: {topic}",
                summary="No evidence was provided. Cannot justify beyond stating insufficient inputs.",
                evidence_refs=[],
                limitations=["Missing evidence input", "Human review required"],
            )

        refs = [f"evidence:{k}" for k in sorted(evidence.keys())]
        return Explanation(
            title=f"Explanation: {topic}",
            summary="This explanation is derived solely from the provided evidence set and known constraints.",
            evidence_refs=refs,
            limitations=[
                "Advisory-only output",
                "No autonomous execution",
                "Subject to human confirmation and permit gate",
            ],
        )
