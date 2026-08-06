# Infrastructure Health Advisor - Infrastructure Layer (Mandatory)
# Output: Recommendations only. No autonomous actions.
# Scope: Kafka, Kubernetes, Network, Storage health signals.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class InfraSignal:
    name: str
    value: float
    unit: str
    ts_epoch: float


@dataclass(frozen=True)
class Recommendation:
    title: str
    severity: str  # LOW/MED/HIGH/CRIT
    rationale: str
    suggested_actions: List[str]
    evidence: Dict[str, Any]


class InfrastructureHealthAdvisor:
    def analyze(self, signals: List[InfraSignal]) -> List[Recommendation]:
        # Fail-closed on empty signals: no guessing.
        if not signals:
            return [
                Recommendation(
                    title="Insufficient telemetry",
                    severity="MED",
                    rationale="No infrastructure signals provided; cannot assess health safely.",
                    suggested_actions=["Verify telemetry pipeline", "Check exporter/collector status"],
                    evidence={"signals_count": 0},
                )
            ]

        # Minimal heuristic set (CTO-grade: explicit, predictable, auditable).
        recs: List[Recommendation] = []
        for s in signals:
            if s.name.lower() in {"kafka_under_replicated_partitions", "kafka_urp"} and s.value > 0:
                recs.append(
                    Recommendation(
                        title="Kafka under-replicated partitions detected",
                        severity="HIGH",
                        rationale="Under-replication increases data-loss risk on broker failure.",
                        suggested_actions=[
                            "Check broker health and ISR shrink events",
                            "Validate rack awareness and broker disk IO",
                            "Consider throttling producers for affected topics",
                        ],
                        evidence={"signal": s.__dict__},
                    )
                )
            if s.name.lower() in {"k8s_node_notready"} and s.value > 0:
                recs.append(
                    Recommendation(
                        title="Kubernetes nodes NotReady",
                        severity="HIGH",
                        rationale="NotReady nodes reduce scheduling capacity and can cause cascading failures.",
                        suggested_actions=[
                            "Investigate node conditions (disk pressure, network)",
                            "Drain/cordon affected nodes and restore capacity",
                            "Validate CNI and storage backend health",
                        ],
                        evidence={"signal": s.__dict__},
                    )
                )

        # If no red flags, still return a bounded, actionable output.
        if not recs:
            recs.append(
                Recommendation(
                    title="Infrastructure appears stable",
                    severity="LOW",
                    rationale="No critical signals breached known thresholds in provided telemetry.",
                    suggested_actions=["Continue monitoring", "Review capacity headroom weekly"],
                    evidence={"signals_count": len(signals)},
                )
            )

        return recs
