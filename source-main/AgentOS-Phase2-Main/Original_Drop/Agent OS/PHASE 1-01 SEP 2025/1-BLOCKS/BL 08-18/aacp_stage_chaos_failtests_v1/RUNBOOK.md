# Fail-Closed Proof Runbook (Phase-1)

Run order (recommended):
1) Baseline negative tests (no fault injection)
2) Inject Policy outage (NetworkPolicy egress deny from Permit) => expect DENY/FAIL
3) Inject Audit outage => expect explicit failure (no silent allow)
4) Inject Kafka outage (Interceptor egress deny) => expect DLQ / controlled failure

What to capture:
- test runner JSON output
- relevant pod logs (intent-gateway, permit-service, audit-sink, kafka-interceptor)
- a screenshot/export of Governance Console showing denied/failure traces

Rollback:
- delete injected NetworkPolicies
- scale audit-sink back to previous replicas
