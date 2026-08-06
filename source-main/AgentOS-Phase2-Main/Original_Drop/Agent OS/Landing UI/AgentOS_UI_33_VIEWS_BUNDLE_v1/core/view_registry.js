const VIEW_REGISTRY = [
  {
    "layer": "os",
    "slug": "governance/overview",
    "title": "Governance Overview",
    "roles": [
      "governance",
      "security",
      "auditor",
      "exec"
    ]
  },
  {
    "layer": "os",
    "slug": "policy/registry",
    "title": "Policy Registry (BL-07)",
    "roles": [
      "governance",
      "security"
    ]
  },
  {
    "layer": "os",
    "slug": "permit/decisions",
    "title": "Permit Decisions (BL-08)",
    "roles": [
      "governance",
      "security",
      "auditor"
    ]
  },
  {
    "layer": "os",
    "slug": "audit/timeline",
    "title": "Audit Timeline (BL-08)",
    "roles": [
      "auditor",
      "governance",
      "security"
    ]
  },
  {
    "layer": "os",
    "slug": "channels/manager",
    "title": "Channel Manager (BL-05)",
    "roles": [
      "governance",
      "security",
      "cto"
    ]
  },
  {
    "layer": "os",
    "slug": "identity/agents",
    "title": "Agent Registry & Identity (BL-06)",
    "roles": [
      "governance",
      "security",
      "cto"
    ]
  },
  {
    "layer": "os",
    "slug": "trust/signatures",
    "title": "Signature & Trust",
    "roles": [
      "security",
      "governance"
    ]
  },
  {
    "layer": "os",
    "slug": "risk/alerts",
    "title": "Operational Risk Alerts",
    "roles": [
      "governance",
      "security",
      "cto",
      "ops"
    ]
  },
  {
    "layer": "os",
    "slug": "compliance/drift",
    "title": "Compliance & Policy Drift",
    "roles": [
      "governance",
      "security",
      "auditor"
    ]
  },
  {
    "layer": "infra",
    "slug": "health/overview",
    "title": "Infrastructure Health",
    "roles": [
      "cto",
      "ops",
      "security"
    ]
  },
  {
    "layer": "infra",
    "slug": "kafka/streams",
    "title": "Kafka Streams",
    "roles": [
      "cto",
      "ops"
    ]
  },
  {
    "layer": "infra",
    "slug": "k8s/namespaces",
    "title": "K8s Namespaces",
    "roles": [
      "cto",
      "ops"
    ]
  },
  {
    "layer": "infra",
    "slug": "capacity/cost",
    "title": "Capacity & Cost",
    "roles": [
      "cto",
      "ops",
      "business"
    ]
  },
  {
    "layer": "infra",
    "slug": "security/posture",
    "title": "Security Posture",
    "roles": [
      "security",
      "cto"
    ]
  },
  {
    "layer": "infra",
    "slug": "resilience/incidents",
    "title": "Resilience Incidents",
    "roles": [
      "ops",
      "cto",
      "security"
    ]
  },
  {
    "layer": "infra",
    "slug": "redteam/findings",
    "title": "RedTeam Findings",
    "roles": [
      "security",
      "cto"
    ]
  },
  {
    "layer": "infra",
    "slug": "observability/metrics",
    "title": "Observability Metrics",
    "roles": [
      "cto",
      "ops",
      "security",
      "auditor"
    ]
  },
  {
    "layer": "domain",
    "slug": "planning/scenarios",
    "title": "Operational Planning Scenarios",
    "roles": [
      "business",
      "exec",
      "governance"
    ]
  },
  {
    "layer": "domain",
    "slug": "performance/variance",
    "title": "Performance Variance",
    "roles": [
      "business",
      "exec"
    ]
  },
  {
    "layer": "domain",
    "slug": "forecast/trends",
    "title": "Forecast & Trends",
    "roles": [
      "business",
      "exec"
    ]
  },
  {
    "layer": "domain",
    "slug": "recommendations/inbox",
    "title": "Recommendations Inbox (BL-13)",
    "roles": [
      "business",
      "exec",
      "governance"
    ]
  },
  {
    "layer": "domain",
    "slug": "correlation/insights",
    "title": "Correlation Insights",
    "roles": [
      "business",
      "exec",
      "governance"
    ]
  },
  {
    "layer": "domain",
    "slug": "kpi/dashboard",
    "title": "Domain KPI Dashboard",
    "roles": [
      "business",
      "exec",
      "governance"
    ]
  },
  {
    "layer": "domain",
    "slug": "risk/heatmap",
    "title": "Risk Heatmap",
    "roles": [
      "business",
      "exec",
      "governance",
      "security"
    ]
  },
  {
    "layer": "domain",
    "slug": "value/impact",
    "title": "Value Impact",
    "roles": [
      "exec",
      "business"
    ]
  },
  {
    "layer": "domain",
    "slug": "history/decisions",
    "title": "Decision History",
    "roles": [
      "exec",
      "business",
      "auditor",
      "governance"
    ]
  },
  {
    "layer": "interaction",
    "slug": "intent/capture",
    "title": "Intent Capture (Text/Voice) (BL-17)",
    "roles": [
      "exec",
      "business",
      "governance",
      "cto",
      "ops",
      "auditor",
      "security"
    ]
  },
  {
    "layer": "interaction",
    "slug": "intent/review",
    "title": "Intent Review & Human Approval",
    "roles": [
      "exec",
      "business",
      "governance",
      "auditor"
    ]
  },
  {
    "layer": "interaction",
    "slug": "explain/why",
    "title": "Explain Why",
    "roles": [
      "exec",
      "business",
      "governance",
      "auditor",
      "security"
    ]
  },
  {
    "layer": "interaction",
    "slug": "narrative/executive",
    "title": "Executive Narrative",
    "roles": [
      "exec",
      "business"
    ]
  },
  {
    "layer": "interaction",
    "slug": "notifications/center",
    "title": "Notification Center",
    "roles": [
      "exec",
      "business",
      "governance",
      "cto",
      "ops",
      "auditor",
      "security"
    ]
  },
  {
    "layer": "interaction",
    "slug": "user/preferences",
    "title": "User Preferences (i18n/RTL)",
    "roles": [
      "exec",
      "business",
      "governance",
      "cto",
      "ops",
      "auditor",
      "security"
    ]
  },
  {
    "layer": "interaction",
    "slug": "session/activity",
    "title": "Session Activity",
    "roles": [
      "auditor",
      "security",
      "governance",
      "cto",
      "ops",
      "exec",
      "business"
    ]
  }
];
