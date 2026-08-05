# Command: /executive-review

**Purpose:** فعال‌سازی فرآیند بازبینی اجرایی و آماده‌سازی پرونده برای کمیته.

**Triggered By:** انسان (مدیرعامل / بنیان‌گذار) یا ایجنت `chief-of-staff`.

**Input Parameters:**
- `decision_package_id`: شناسه بسته تصمیم (تولیدشده توسط `prepare-decision`)

**Action Flow:**
1. فعال‌سازی ایجنت `chief-of-staff`
2. فراخوانی مهارت `executive-decision-package`
3. بازبینی نهایی محتوا و ارسال به کمیته ZDC

**Output:** فایل `final_executive_package_[timestamp].md` در پوشه `workflows/executive-review/`.
