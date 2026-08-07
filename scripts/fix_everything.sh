#!/bin/bash
echo "🔄 تعمیر بنیادین مسیریابی و آدرس‌دهی UI..."

# ۱. اصلاح ریشه‌ای view-registry.json برای مطابقت با لینک‌های ناوبری
cat > ui/core/view-registry.json << 'EOF'
{
  "os/os-dashboard": {
    "html": "../views/os/os-dashboard.html",
    "js": "../views/os/os-dashboard.js"
  },
  "os/os-governance-console": {
    "html": "../views/os/os-governance-console.html",
    "js": "../views/os/os-governance-console.js"
  },
  "os/os-policy-browser": {
    "html": "../views/os/os-policy-browser.html",
    "js": "../views/os/os-policy-browser.js"
  },
  "os/os-permit-review": {
    "html": "../views/os/os-permit-review.html",
    "js": "../views/os/os-permit-review.js"
  },
  "os/os-audit-trace": {
    "html": "../views/os/os-audit-trace.html",
    "js": "../views/os/os-audit-trace.js"
  },
  "os/os-channel-manager": {
    "html": "../views/os/os-channel-manager.html",
    "js": "../views/os/os-channel-manager.js"
  },
  "os/os-agent-registry": {
    "html": "../views/os/os-agent-registry.html",
    "js": "../views/os/os-agent-registry.js"
  },
  "infra/infra-overview": {
    "html": "../views/infra/infra-overview.html",
    "js": "../views/infra/infra-overview.js"
  },
  "infra/infra-kafka": {
    "html": "../views/infra/infra-kafka-health.html",
    "js": "../views/infra/infra-kafka-health.js"
  },
  "infra/infra-k8s-topology": {
    "html": "../views/infra/infra-k8s-topology.html",
    "js": "../views/infra/infra-k8s-topology.js"
  },
  "infra/infra-security-posture": {
    "html": "../views/infra/infra-security-posture.html",
    "js": "../views/infra/infra-security-posture.js"
  },
  "domain/domain-recommendations": {
    "html": "../views/domain/domain-recommendations.html",
    "js": "../views/domain/domain-recommendations.js"
  },
  "domain/domain-scenario-planner": {
    "html": "../views/domain/domain-scenario-planner.html",
    "js": "../views/domain/domain-scenario-planner.js"
  },
  "interaction/interaction-intent-input": {
    "html": "../views/interaction/interaction-intent-input.html",
    "js": "../views/interaction/interaction-intent-input.js"
  },
  "interaction/interaction-exec-approval": {
    "html": "../views/interaction/interaction-exec-approval.html",
    "js": "../views/interaction/interaction-exec-approval.js"
  }
}
