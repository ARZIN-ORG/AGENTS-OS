AACP / Agent OS — Step 8 (Control Plane Freeze) — v1.0
Generated: 2026-01-06 19:41

این بسته «قدم ۸» را تحویل می‌دهد: تثبیت و قفل‌کردن Control Plane به‌عنوان مرجع اجرایی فاز ۱، با جداسازی قطعی Control Plane و Data Plane، و تعریف مرزهای غیرقابل دور زدن.

محتویات:
1) AGENT_OS_V1_FREEZE.md — تعریف دقیق اینکه Agent OS v1 چه می‌کند و چه کارهایی را عمداً نمی‌کند.
2) CONTROL_DATA_PLANE_CONTRACT.md — قرارداد جداسازی Control Plane / Data Plane و قوانین عبور.
3) ADR-001_AGENTOS_V1_FREEZE.md — ADR رسمی تصمیم قفل نسخه.
4) REFERENCE_ARCHITECTURE.mmd — دیاگرام مرجع (Mermaid) برای مستندسازی و رندر در Git.
5) THREAT_MODEL_SUMMARY.md — Threat model خلاصه و CTO-پسند (Fail-Closed, No-Bypass).
6) RELEASE_PLAN_LOCK.md — قفل Release Plan فاز ۱ با DoD و گیت‌های کیفی.

نکته عملی: این قدم «قابلیت جدید» اضافه نمی‌کند. این قدم جلوی دوباره‌کاری و تفسیرپذیری را می‌گیرد.
