# BL-08 — Permit Service (Decision Gate) — Architecture v1
شناسه: ARZIN-AOS-BL08-PERMIT-ARCH-v1.0
دامنه: فاز ۱ سیستم‌عامل ایجنت‌ها (Agent OS)

## نقش
Permit Service آخرین گیت حاکمیتی قبل از عبور پیام در Data Plane است.
این سرویس هیچ تصمیم هوشمند، یادگیری یا اجرا انجام نمی‌دهد.
خروجی فقط ALLOW یا DENY با دلیل قابل audit است.

## قیود قفل‌شده
- فقط observe / recommend مجاز است
- Fail-Closed: عدم پاسخ = Reject
- تصمیم مستقل از Agent (Agent تصمیم نمی‌گیرد)
- استقرار Private Cloud
- تصمیم deterministic و قابل بازسازی

## جریان تصمیم
1. دریافت PermitRequest از Interceptor
2. اعتبارسنجی Envelope (signature_valid, ttl, payload_size)
3. Lookup Agent Registry (BL-06)
4. Lookup Effective Policy (BL-07)
5. اعمال Constraints
6. صدور PermitDecision + trace

## خروجی
PermitDecision شامل:
- decision: ALLOW | DENY
- reason_code
- policy_id / version
- agent_id
- trace_id
