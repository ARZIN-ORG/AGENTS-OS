Threat Model Summary — Agent OS v1 (Phase 1)

هدف
این Threat Model روی حملات و شکست‌هایی تمرکز می‌کند که در غیاب Control Plane، سیستم را از «قابل حسابرسی» به «غیرقابل دفاع» تبدیل می‌کنند.

دارایی‌های حیاتی
زنجیره مجوز و تأیید انسانی، Audit Trail، امضای پیام و هویت عامل، نسخه Policy و کانال مجاز.

سطح حمله اصلی
Publish مستقیم پیام عملیاتی بدون Permit. جعل هویت Agent. دستکاری Payload یا متادیتا. Replay پیام. دور زدن Audit. Policy drift در محیط اجرا. خطاهای زیرساختی که باعث Fail-Open شوند.

کنترل‌های قطعی (Fail-Closed)
اگر Signature verifier شکست بخورد، Reject. اگر Registry یا Policy یا Permit در دسترس نباشد، Reject. اگر Audit Sink در دسترس نباشد، Reject. اگر channel_id نامعتبر باشد، Reject. اگر chain hash تولید نشود، Reject. اگر Intent تأیید انسانی نداشته باشد، Permit صادر نمی‌شود.

کنترل‌های کاهش ریسک
حداقل‌سازی دسترسی Topicها بر اساس ABAC/Scope. جداسازی نقش‌ها (Policy Author ≠ Developer ≠ Operator ≠ Auditor). چرخش کلید و گواهی در دوره مشخص. Rate-limit و quota برای جلوگیری از flood. DLQ ساختاریافته و قابل ممیزی.

معیار پذیرش امنیتی (Gate)
هر سناریوی bypass باید در Test Harness شکست بخورد. هیچ مسیر Fail-Open قابل قبول نیست. هر پیام عملیاتی باید قابل ردیابی end-to-end باشد.
