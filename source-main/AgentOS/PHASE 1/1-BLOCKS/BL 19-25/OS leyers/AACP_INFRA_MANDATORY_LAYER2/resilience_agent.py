# Resilience Agent - Infrastructure Layer (Mandatory)
# Output: Recommendations/playbook steps only. No autonomous failover.
# Scope: Failover guidance, recovery hypotheses, resilience posture.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class IncidentSignal:
    component: str
    symptom: str
    ts_epoch: float
    evidence: Dict[str, Any]


@dataclass(frozen=True)
class PlaybookStep:
    step: int
    action: str
    guardrails: str
    expected_outcome: str


@dataclass(frozen=True)
class ResilienceAdvice:
    title: str
    severity: str
    rationale: str
    steps: List[PlaybookStep]
    evidence: Dict[str, Any]


class ResilienceAgent:
    def propose_recovery(self, signals: List[IncidentSignal]) -> List[ResilienceAdvice]:
        if not signals:
            return [
                ResilienceAdvice(
                    title="No incident signals provided",
                    severity="MED",
                    rationale="Cannot propose recovery without observed symptoms and evidence.",
                    steps=[
                        PlaybookStep(
                            step=1,
                            action="Verify monitoring and alert pipeline",
                            guardrails="No production changes without human approval",
                            expected_outcome="Confirm incident context exists",
                        )
                    ],
                    evidence={"signals_count": 0},
                )
            ]

        advices: List[ResilienceAdvice] = []
        for s in signals:
            if s.component.lower() == "kafka" and "broker" in s.symptom.lower():
                advices.append(
                    ResilienceAdvice(
                        title="Kafka broker instability: recovery proposal",
                        severity="HIGH",
                        rationale="Broker instability can cascade into producer/consumer backlog and DLQ spikes.",
                        steps=[
                            PlaybookStep(1, "Confirm broker health and ISR status", "Read-only checks first", "Known faulty broker(s) identified"),
                            PlaybookStep(2, "Drain traffic / reduce producer rate on impacted topics", "Apply only via approved channel", "Backpressure reduced"),
                            PlaybookStep(3, "Execute broker restart/replace using HA playbook", "Human approval required", "Cluster returns to stable ISR"),
                        ],
                        evidence={"signal": s.__dict__},
                    )
                )

        if not advices:
            advices.append(
                ResilienceAdvice(
                    title="Generic resilience check",
                    severity="LOW",
                    rationale="No mapped recovery template matched; provide safe baseline steps.",
                    steps=[
                        PlaybookStep(1, "Collect timeline and correlate alerts", "No changes yet", "Incident scope clarified"),
                        PlaybookStep(2, "Identify single-point pressure (CPU/IO/queue)", "No action without permit", "Candidate bottleneck identified"),
                    ],
                    evidence={"signals_count": len(signals)},
                )
            )

        return advices
