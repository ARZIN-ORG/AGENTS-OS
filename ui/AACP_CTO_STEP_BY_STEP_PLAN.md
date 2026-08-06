# برنامه قدم‌به‌قدم برای جلسه با CTO — سیم‌کشی واقعی، GameDay و Shadow Pilot (Phase‑1)
نسخه: v1.0
تاریخ: 2026-01-07
مالک: Agent OS / AACP

## 0) هدف جلسه
این جلسه برای «ساخت قابلیت جدید» نیست. هدف، بستن سه حلقه است: سیم‌کشی واقعی (بدون Mock)، اثبات عملی حاکمیت با GameDay، و آماده‌سازی Shadow Pilot کم‌ریسک.

## 1) تصمیم‌های قفل‌شده (برای جلوگیری از بحث تکراری)
در Phase‑1 و Phase‑2 هیچ ایجنتی تصمیم نهایی یا اجرای خودکار ندارد. سیستم فقط Recommendation می‌دهد و اجرا فقط بعد از تأیید انسان و Permit انجام می‌شود. ورودی Voice/Text هیچ‌وقت مستقیم AACP publish نمی‌کند. مسیر الزام‌آور همین است: MFA → دریافت Voice/Text → Intent → نمایش به انسان → اصلاح/رد/تأیید → Permit → Publish از مسیر AACP → Audit/Trace → گزارش مدیریتی.

## 2) وضعیت فعلی (واقعیت، نه روایت)
هسته‌های BL تا BL‑08 آماده‌اند و برای Private Cloud بسته‌های استقرار/هاردنینگ داریم. UI/UX حاکمیتی (Light/Dark) آماده است و نسخه دو زبانه (FA/EN) با RTL/LTR هم آماده شده است. دو سند «GameDay Playbook» و «External Regulatory Narrative» تولید شده‌اند. یک بسته “Wired Real Mode” برای UI+BFF آماده شده که مسیر Mock را در حالت Real خاموش می‌کند.

## 3) خروجی مورد انتظار فردا
خروجی فردا باید سه چیز باشد. اول، چک‌لیست نهایی سیم‌کشی واقعی با SSO/RBAC. دوم، زمان‌بندی اجرای یک GameDay کوچک (S1 تا S5). سوم، انتخاب دامنه Shadow Pilot و مرزهای ریسک آن.

## 4) قدم 1 — تعیین استاندارد SSO/RBAC و Token Contract
باید مشخص شود سها OIDC دارد یا SAML. UI فقط مصرف‌کننده توکن است و تصمیم امنیتی داخل UI نداریم. توکن باید شامل role و scope باشد. نقش‌ها حداقل این‌ها هستند: Viewer، Reviewer، Approver، Auditor، Operator. هر اکشن UI باید role-gated باشد و بدون claim معتبر Fail شود.

## 5) قدم 2 — تعریف توپولوژی سرویس‌ها و مسیر ارتباطی UI
UI نباید مستقیم به سرویس‌های BL وصل شود. یک BFF لازم است با نام governance-console-api. UI فقط به BFF می‌زند. BFF پشت صحنه به BL‑06/07/08/17/19 وصل می‌شود و RBAC را enforce می‌کند. این طراحی خطا را متمرکز می‌کند و نقطه کنترل می‌دهد.

## 6) قدم 3 — لیست Endpointهای واقعی که باید Wire شوند
برای فردا، فقط این موارد را می‌خواهیم و بقیه را عقب می‌اندازیم.
BL‑06: لیست ایجنت‌ها، وضعیت، نسخه، owner، domain، identity.
BL‑07: resolve policy برای intent، دریافت policy version و constraints.
BL‑08: درخواست permit، review/approve، ثبت trace و بازیابی trace.
BL‑17: submit intent پیشنهادی، preview، و تبدیل intent به درخواست permit.
BL‑19: عملیات کنسول (جمع‌بندی وضعیت، گزارش‌ها، لیست تصمیم‌ها).

## 7) قدم 4 — حذف Mock با Feature Flag و Fail‑Safe
در محیط واقعی، Mock ممنوع است. فقط یک Feature Flag برای demo باقی می‌ماند. Default در Private Cloud باید REAL_MODE باشد و اگر Backend/Auth نبود، UI باید خطا بدهد، نه data جعلی.

## 8) قدم 5 — اتصال KeyStore/HSM برای Signature Verification
تا زمانی که Signature Verifier به KeyStore واقعی وصل نشود، امنیت ادعایی است. برای Phase‑1 دو مسیر قابل قبول است: HSM یا File‑Keystore امن در Private Cloud با Rotation و ACL. CTO باید انتخاب کند کدام مسیر در این هفته انجام می‌شود.

## 9) قدم 6 — قفل Audit Envelope و Chain Hash در مسیر عملیاتی
باید تأیید شود که Audit Envelope به‌صورت اجباری در interceptor validate می‌شود و هر پیام بدون Envelope/ChainHash رد می‌شود. همچنین باید مشخص شود Audit Sink stateful است و append-only. هیچ موفقیتی بدون ثبت Audit پایدار قبول نیست.

## 10) قدم 7 — تعریف GameDay کوچک (۵ سناریو اول)
فردا باید CTO با اجرای GameDay روی این پنج سناریو موافقت کند: S1 مسیر سالم، S2 مسیر Voice، S3 بدون Permit، S4 Policy mismatch، S5 Signature fail. هر سناریو باید TraceID و PermitID و PolicyVersion و ChainHash تولید کند. معیار قبول/رد باید قبل از اجرا امضا شود.

## 11) قدم 8 — تعریف بسته Evidence برای حسابرسی داخلی
Evidence Pack شامل این‌هاست: خروجی Trace برای هر سناریو، رویدادهای DLQ، لاگ interceptor، لاگ permit، و Head/Tail chain hash. این بسته باید immutable archive شود و به تیم حاکمیت ارائه شود.

## 12) قدم 9 — تعریف Shadow Pilot (کم‌ریسک و کنترل‌شده)
Shadow Pilot یعنی read-only یا recommendation-only. بدون marketplace. بدون auto-execution. فقط یک دامنه محدود با حجم پایین. هدف، تست رفتار واقعی در عملیات بدون ریسک حقوقی است. CTO باید دامنه را انتخاب کند و «حداکثر دامنه اثر» را امضا کند.

## 13) قدم 10 — تقسیم کار بین DevOps/Backend/Frontend
DevOps: استقرار K8s/Kafka، mTLS، secrets، cert rotation، observability، immutable storage.
Backend: BFF و wiring به BLها، RBAC enforcement، policy/permit orchestration.
Frontend: اتصال UI به BFF، i18n و RTL/LTR، role-gating، خطاهای fail-safe، و گزارش مدیریتی.

## 14) خروجی جلسه (چک‌لیست امضا)
در پایان جلسه باید این‌ها امضا شوند: انتخاب SSO استاندارد، توپولوژی BFF، لیست endpointهای wired، سیاست Mock=OFF در Real، انتخاب KeyStore/HSM، دامنه GameDay و معیار قبول/رد، و دامنه Shadow Pilot.

## 15) ضمیمه: فایل‌های موجود برای جلسه
- GameDay Playbook (Phase‑1)
- External Regulatory Narrative (Phase‑1)
- UI بسته Light/Dark (Bilingual)
- UI Wired Real Mode Bundle + BFF
