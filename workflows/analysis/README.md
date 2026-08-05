# Workflow: Analysis

**مرحله:** ۱ از ۶
**وضعیت:** شروع گردش کار

**ورودی:** فراخوانی `/analyze` توسط انسان یا سیستم.

**فرآیند:**
1. ایجنت مرتبط (`strategy-investment` و `supply-chain`) داده‌های ورودی را دریافت می‌کنند.
2. مهارت `analysis` فراخوانی می‌شود.
3. گزارش تحلیل خام تولید می‌شود.

**خروجی:** فایل `analysis_report_[timestamp].md` که به مرحله بعد (`workflows/recommendation/`) ارسال می‌شود.
