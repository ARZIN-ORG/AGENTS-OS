# نقاب‌کِش (Drift/Anomaly Detector) - Infrastructure Layer (Mandatory)
# Output: Detection + recommendations only. No autonomous action.
# Purpose: Detect silent drift/anomalies that bypass obvious alerts.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class DriftEvent:
    key: str
    before: Any
    after: Any
    ts_epoch: float
    evidence: Dict[str, Any]


@dataclass(frozen=True)
class DriftAlert:
    title: str
    severity: str
    rationale: str
    suggested_actions: List[str]
    evidence: Dict[str, Any]


class NeghabKesh:
    def detect(self, events: List[DriftEvent]) -> List[DriftAlert]:
        if not events:
            return [
                DriftAlert(
                    title="No drift events provided",
                    severity="LOW",
                    rationale="No configuration drift input received.",
                    suggested_actions=["Keep drift collection enabled"],
                    evidence={"events_count": 0},
                )
            ]

        alerts: List[DriftAlert] = []
        for e in events:
            # Simple but auditable: any change in critical keys is flagged.
            if e.key.lower() in {"kafka.min.insync.replicas", "kafka.acks", "k8s.networkpolicy", "mtls.enforced"}:
                alerts.append(
                    DriftAlert(
                        title=f"Critical drift detected: {e.key}",
                        severity="HIGH",
                        rationale="Critical configuration changed; requires governance review and audit proof.",
                        suggested_actions=[
                            "Verify change ticket / approval",
                            "Rollback via approved change path if unauthorized",
                            "Attach drift evidence to immutable audit trail",
                        ],
                        evidence={"drift": e.__dict__},
                    )
                )

        if not alerts:
            alerts.append(
                DriftAlert(
                    title="No critical drift detected",
                    severity="LOW",
                    rationale="No changes matched critical drift keys set.",
                    suggested_actions=["Continue monitoring drift keys"],
                    evidence={"events_count": len(events)},
                )
            )
        return alerts
