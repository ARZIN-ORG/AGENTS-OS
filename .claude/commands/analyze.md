# Command: /analyze

**Purpose:** راه‌اندازی فرآیند تحلیل داده، بررسی وضعیت بازار و شبیه‌سازی سناریوها.

**Triggered By:** انسان (مدیرعامل / بنیان‌گذار) یا فرآیند زمان‌بندی‌شده خودکار.

**Input Parameters:**
- `target`: موضوع یا حوزه مورد تحلیل (مثلاً: "بازار EV ایران" یا "ریسک تأمین‌کننده چین")
- `scope`: محدوده زمانی یا عمق تحلیل (مثلاً: "۳ ماه گذشته" یا "پیش‌بینی ۱ سال آینده")

**Action Flow:**
1. فعال‌سازی ایجنت `strategy-investment` و `supply-chain`
2. فراخوانی مهارت `analysis`
3. تولید و ثبت گزارش اولیه در `.claude/skills/analysis/`

**Output:** فایل `analysis_report_[timestamp].md` در پوشه `workflows/analysis/`.
