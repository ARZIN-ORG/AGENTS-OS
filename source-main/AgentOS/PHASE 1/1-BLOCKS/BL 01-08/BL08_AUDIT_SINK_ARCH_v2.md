# BL-08 — Audit Sink Service v2 (Phase-1)
شناسه: ARZIN-AOS-BL08-AUDIT-SINK-v2.0

## هدف
Audit Sink مقصد نهایی ثبت تصمیم‌های حاکمیتی AACP است.
این سرویس «لاگ متنی» نیست؛ ذخیره‌ساز ساخت‌یافته و قابل Query است.

## قیود قفل‌شده
در فاز ۱ و ۲ هیچ ایجنتی تصمیم نمی‌گیرد.
Audit Sink فقط شواهد را ثبت می‌کند و قابلیت بازسازی را فراهم می‌کند.
Fail-fast / Reject: اگر ثبت Audit شکست بخورد، مسیر باید Fail-Closed شود.

## ورودی
AacpAuditRecord شامل:
- trace_id, message_id, channel_id, topic
- agent_id, agent_class
- policy_id, policy_version
- decision (ALLOW/DENY) + reason_code
- envelope_hash / chain_hash (اختیاری ولی توصیه‌شده)
- timestamps (event_time, received_time)
- signature_valid (برای forensic)

## خروجی
- ACK ذخیره موفق
- Query endpoint برای بازیابی record بر اساس trace_id و message_id

## ذخیره‌سازی
پیش‌فرض SQLite برای توسعه.
برای Private Cloud: PostgreSQL با DATABASE_URL.
