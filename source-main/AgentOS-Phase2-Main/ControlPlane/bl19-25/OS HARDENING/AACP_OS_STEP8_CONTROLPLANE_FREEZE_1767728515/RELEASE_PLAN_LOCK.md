قفل Release Plan فاز ۱ — بعد از Step 7

هدف
این سند تعیین می‌کند بعد از Step 7 چه چیزهایی در فاز ۱ مجاز است و چه چیزهایی مجاز نیست تا دوباره‌کاری و انفجار دامنه رخ ندهد.

مجاز
سفت‌کردن Control Plane، بهبود کیفیت Audit، افزایش پوشش تست‌های شکست، بهبود observability، بهبود wiring با Kafka و mTLS و rotation، و اصلاحات performance که رفتار Fail-Closed را تغییر ندهد.

غیرمجاز
افزودن Agentهای جدید که به Topic عملیاتی publish کنند. افزودن مسیر اجرای خودکار. افزودن Marketplace یا onboarding بیرونی بدون کنترل‌های کامل Registry/Policy/Permit/Audit. تغییرات شکستننده در Audit Envelope یا Schema بدون نسخه‌بندی رسمی و مهاجرت.

DoD Release فاز ۱
Test Harness باید همه سناریوهای Reject و Fail-Closed را پاس کند. هیچ پیام عملیاتی بدون Permit نباید publish شود. Audit Sink باید stateful و پایدار باشد. Chain hash باید تولید شود و در audit ذخیره شود. مستندات این بسته باید در ریپازیتوری و مسیر CI گیت شود.
