# Observability Checklist v1 — AACP Phase-1

Metrics حداقلی:
aacp_allow_total, aacp_deny_total, aacp_fail_closed_total, aacp_audit_persist_fail_total
aacp_permit_latency_ms(p95), aacp_registry_latency_ms(p95), aacp_policy_latency_ms(p95)
aacp_dlq_publish_fail_total

Logs حداقلی:
trace_id, message_id, channel_id, topic, agent_id, decision, reason_code
status_codeهای BL-06/07/08 و Audit Sink

Alerts حداقلی:
deny_rate spike
fail_closed spike
audit_persist_fail > 0
permit_latency p95 بالا
