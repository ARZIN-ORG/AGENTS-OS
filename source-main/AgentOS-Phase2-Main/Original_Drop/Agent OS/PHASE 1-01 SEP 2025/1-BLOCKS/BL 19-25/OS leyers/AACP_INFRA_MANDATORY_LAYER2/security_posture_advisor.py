# Security Posture Advisor - Infrastructure Layer (Mandatory)
# Output: Recommendations only. No autonomous changes.
# Scope: Misconfiguration, drift, exposure indicators.

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class SecurityFinding:
    control: str
    status: str  # PASS/FAIL/WARN
    detail: str
    evidence: Dict[str, Any]


@dataclass(frozen=True)
class SecurityRecommendation:
    title: str
    severity: str
    rationale: str
    suggested_actions: List[str]
    evidence: Dict[str, Any]


class SecurityPostureAdvisor:
    def assess(self, findings: List[SecurityFinding]) -> List[SecurityRecommendation]:
        if not findings:
            return [
                SecurityRecommendation(
                    title="No security findings provided",
                    severity="MED",
                    rationale="Cannot assess posture without explicit controls and evidence.",
                    suggested_actions=["Run baseline posture scan", "Export controls to audit sink"],
                    evidence={"findings_count": 0},
                )
            ]

        recs: List[SecurityRecommendation] = []
        for f in findings:
            if f.status == "FAIL":
                recs.append(
                    SecurityRecommendation(
                        title=f"Control failed: {f.control}",
                        severity="HIGH",
                        rationale=f"Security control failed: {f.detail}",
                        suggested_actions=[
                            "Apply configuration remediation via approved change process",
                            "Re-run scan and attach evidence to immutable audit",
                        ],
                        evidence={"finding": f.__dict__},
                    )
                )
            elif f.status == "WARN":
                recs.append(
                    SecurityRecommendation(
                        title=f"Control warning: {f.control}",
                        severity="MED",
                        rationale=f"Potential drift or partial compliance: {f.detail}",
                        suggested_actions=[
                            "Validate drift source (config, version, operator action)",
                            "Harden baseline and enforce via policy plane",
                        ],
                        evidence={"finding": f.__dict__},
                    )
                )

        if not recs:
            recs.append(
                SecurityRecommendation(
                    title="Security posture baseline: OK",
                    severity="LOW",
                    rationale="No FAIL/WARN controls detected in provided evidence.",
                    suggested_actions=["Keep continuous scanning enabled"],
                    evidence={"findings_count": len(findings)},
                )
            )
        return recs
