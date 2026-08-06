ADR-001 — Freeze Agent OS v1 (Phase 1 Control Plane)

شناسه: ARZIN-AGENTOS-STEP8-v1.0
وضعیت: Accepted (Locked for Phase 1)
تاریخ: 2026-01-06 19:41

زمینه
در سیستم‌های عامل‌محور، بزرگ‌ترین ریسک «تکثیر مسیرهای تصمیم و اجرا» است. اگر Control Plane قبل از رشد اکوسیستم قفل نشود، سیستم به‌جای نوآوری، هرج‌ومرج تولید می‌کند و Audit از کار می‌افتد.

تصمیم
Agent OS v1 برای فاز ۱ به‌عنوان Control Plane حاکمیتی قفل می‌شود. هیچ تصمیم خودکار مجاز نیست. همه مسیرها Human-in-the-loop دارند و اجرا فقط پس از Permit معتبر و ثبت Audit انجام می‌شود. جداسازی Control Plane و Data Plane قطعی و غیرقابل bypass است.

پیامدها
توسعه ویژگی‌ها در کوتاه‌مدت کندتر به نظر می‌رسد، اما هزینه بازنویسی و incidentهای غیرقابل توضیح در آینده کاهش شدید پیدا می‌کند. هر سرویس یا Agent جدید باید در مرزهای این ADR قرار گیرد یا وارد فاز ۲ شود.

گزینه‌های ردشده
توسعه Marketplace قبل از قفل Control Plane رد شد. اجازه publish مستقیم از Interaction یا Agentهای Domain رد شد. تکیه بر logهای best-effort به‌جای Audit immutable رد شد.

DoD
Release وقتی پذیرفته می‌شود که Test Harness سناریوهای bypass و fail را رد کند، و همه پیام‌های عملیاتی Audit Envelope و Permit معتبر داشته باشند.
