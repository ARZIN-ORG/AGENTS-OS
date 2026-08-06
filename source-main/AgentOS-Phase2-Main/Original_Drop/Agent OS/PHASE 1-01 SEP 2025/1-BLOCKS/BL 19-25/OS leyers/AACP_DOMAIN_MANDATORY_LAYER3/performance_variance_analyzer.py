# Performance Variance Analyzer - Domain Layer (Mandatory)
# Output: Actionable variance insights only. No autonomous decisions/execution.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class MetricPoint:
    unit_id: str
    metric: str
    value: float
    ts_epoch: float


@dataclass(frozen=True)
class VarianceInsight:
    title: str
    severity: str
    rationale: str
    top_drivers: List[str]
    suggested_investigation: List[str]
    evidence: Dict[str, Any]


class PerformanceVarianceAnalyzer:
    def analyze(self, points: List[MetricPoint]) -> List[VarianceInsight]:
        if not points:
            return [
                VarianceInsight(
                    title="No metrics provided",
                    severity="LOW",
                    rationale="No data points received for variance analysis.",
                    top_drivers=[],
                    suggested_investigation=["Verify metrics collection and unit_id mapping"],
                    evidence={"points_count": 0},
                )
            ]

        # Simple baseline: group by metric and show range dispersion.
        by_metric: Dict[str, List[MetricPoint]] = {}
        for p in points:
            by_metric.setdefault(p.metric, []).append(p)

        insights: List[VarianceInsight] = []
        for metric, arr in by_metric.items():
            values = [x.value for x in arr]
            vmin, vmax = min(values), max(values)
            spread = vmax - vmin
            if spread <= 0:
                continue
            severity = "LOW"
            if spread > (0.3 * max(1.0, vmax)):
                severity = "MED"
            if spread > (0.6 * max(1.0, vmax)):
                severity = "HIGH"

            insights.append(
                VarianceInsight(
                    title=f"Variance detected for {metric}",
                    severity=severity,
                    rationale=f"Observed spread={spread:.3f} between units for metric={metric}.",
                    top_drivers=[
                        "Data quality differences",
                        "Operational practice differences",
                        "Infrastructure locality effects",
                    ],
                    suggested_investigation=[
                        "Validate input data consistency across units",
                        "Correlate with environment/conditions and process changes",
                        "Check for outliers and measurement drift",
                    ],
                    evidence={
                        "metric": metric,
                        "min": vmin,
                        "max": vmax,
                        "spread": spread,
                        "units": list({x.unit_id for x in arr}),
                    },
                )
            )

        if not insights:
            insights.append(
                VarianceInsight(
                    title="No variance signal above baseline",
                    severity="LOW",
                    rationale="Metrics do not show meaningful dispersion in provided dataset.",
                    top_drivers=[],
                    suggested_investigation=["Increase sample size / time window", "Check metric definitions"],
                    evidence={"metrics_count": len(by_metric)},
                )
            )

        return insights
