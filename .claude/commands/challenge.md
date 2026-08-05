# Command: /challenge

**Purpose:** فعال‌سازی فرآیند به چالش کشیدن پیشنهادات و شناسایی ریسک‌های پنهان.

**Triggered By:** انسان (مدیرعامل / بنیان‌گذار) یا کمیته ZDC.

**Input Parameters:**
- `proposal_id`: شناسه پیشنهاد یا تصمیم مورد نظر
- `assumptions`: مفروضاتی که باید به‌چالش کشیده شوند

**Action Flow:**
1. فعال‌سازی ایجنت‌های `independent-advisor` و `risk-contradiction`
2. فراخوانی مهارت `challenge`
3. تحلیل سناریوی بدترین حالت و تولید گزارش مخالف

**Output:** فایل `challenge_report_[timestamp].md` در پوشه `workflows/challenge/`.
