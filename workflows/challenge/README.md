# Workflow: Challenge

**مرحله:** ۳ از ۶
**وضعیت:** پس از Recommendation

**ورودی:** فایل `recommendation_[timestamp].md` و فراخوانی `/challenge`.

**فرآیند:**
1. ایجنت‌های `independent-advisor` و `risk-contradiction` پیشنهاد را بررسی می‌کنند.
2. مهارت `challenge` فراخوانی می‌شود.
3. ریسک‌های پنهان شناسایی و یک گزینه جایگزین پیشنهاد می‌شود.

**خروجی:** فایل `challenge_report_[timestamp].md` که به مرحله بعد (`workflows/executive-review/`) ارسال می‌شود.
