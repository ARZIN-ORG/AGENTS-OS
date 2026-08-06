# SOHA Wiring Runbook v1 — AACP Phase-1 (Fail-Closed)

هدف: Hook باید قبل از publish اجرا شود. بعد از آن Audit ثبت شود. DENY/FAIL به DLQ برود.

نقطه اتصال: Producer Interceptor اولویت دارد. Sidecar گزینه دوم است. Gateway تنها کافی نیست.

قانون Fail-Closed: نبود Registry/Policy/Permit یا شکست Audit Persist یا شکست DLQ publish => Reject.

پارامترها: REGISTRY_URL, POLICY_URL, PERMIT_URL, AUDIT_SINK_URL, KAFKA_BOOTSTRAP_SERVERS, DLQ_TOPIC, CACHE_TTL_MS, FAIL_CLOSED=true

DoD:
1) همه سرویس‌ها /health OK.
2) پیام معتبر: ALLOW، publish انجام شود، audit ثبت شود.
3) پیام نامعتبر: DENY، publish نشود، DLQ event ثبت شود، audit ثبت شود.
4) Audit Sink down: publish نشود (Fail-Closed).
5) Permit down: publish نشود (Fail-Closed).
