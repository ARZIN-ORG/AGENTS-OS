# Chaos Runbook v1 — AACP Phase-1 (Fail-Closed Proof)

هدف: ثابت کنیم Fail-Closed واقعی است و دورزدن ندارد.

سناریوها:
1) Permit down: scale deployment permit-service to 0.
   انتظار: publish در SOHA reject شود و fail_closed افزایش یابد.
2) Policy down: scale policy-plane to 0.
   انتظار: reject و fail_closed.
3) Registry down: scale agent-registry to 0.
   انتظار: reject و fail_closed.
4) Audit down: scale audit-sink to 0.
   انتظار: reject و fail_closed. هیچ پیام نباید عبور کند.
5) DLQ down (Kafka unreachable): قطع دسترسی hook به Kafka.
   انتظار: هر DENY باید reject بماند چون DLQ publish شکست می‌خورد.

شواهد لازم:
- افزایش aacp_fail_closed_total
- لاگ hook با reason_code مشخص
- نبود پیام در topic مقصد در زمان outage
