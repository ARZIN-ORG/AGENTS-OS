# Command: /prepare-decision

**Purpose:** بسته‌بندی تمامی تحلیل‌ها، پیشنهادها و گزارش‌های مخالف برای رأی‌گیری نهایی.

**Triggered By:** انسان (مدیرعامل / بنیان‌گذار) یا کمیته ZDC.

**Input Parameters:**
- `analysis_id`: شناسه گزارش تحلیل
- `recommendation_id`: شناسه پیشنهاد اولیه
- `challenge_id`: شناسه گزارش چالش

**Action Flow:**
1. تجمیع خروجی‌های `analysis`، `recommendation` و `challenge`
2. فعال‌سازی مهارت `executive-decision-package`
3. آماده‌سازی بسته نهایی تصمیم

**Output:** فایل `decision_package_[timestamp].md` در پوشه `workflows/decision/`.
