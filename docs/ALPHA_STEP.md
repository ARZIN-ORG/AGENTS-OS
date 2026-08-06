بسیار خوب. بر اساس تمام مراحل طی‌شده، از استخراج کدها تا مهاجرت نهایی، تست‌ها و یکپارچه‌سازی، مستند «گام آلفا (Alpha Step)» را به‌عنوان راهنمای نهایی و جامع برای استقرار و بهره‌برداری از سیستم عامل ایجنت AGENTS-OS تهیه کرده‌ام. این مستند پس از اتمام تمام آزمون‌ها و تست‌ها، به‌عنوان مرجع عملیاتی و فنی کامل اجرا می‌شود.

---

📜 گام آلفا (Alpha Step) – مستند نهایی استقرار و عملیاتی‌سازی AgentOS

نسخه: v1.0.0-rc2
تاریخ: ۲۰۲۶-۰۸-۰۶
وضعیت: نهایی – آماده‌ی اجرا پس از تأیید تست‌ها
هدف: ارائه‌ی نقشه‌ی کامل، گام‌به‌گام و فنی برای راه‌اندازی، تست و تحویل سیستم عامل ایجنت AGENTS-OS.

---

۱. مقدمه و هدف

سیستم عامل ایجنت AGENTS-OS یک پلتفرم ارکستراسیون رویدادمحور برای اجرای سازمان‌های ایجنت‌محور است. این سیستم، تعاریف انتزاعی ایجنت‌ها را از طریق کامپایلر خودکار به توپیک‌های کافکا و سرویس‌های پایتون متصل می‌کند و یک داشبورد نظارت انسانی ارائه می‌دهد. مستند «گام آلفا» شامل تمام جزئیات فنی، ساختار، دستورات و آزمون‌های نهایی است که پس از اتمام مراحل توسعه و یکپارچه‌سازی، باید اجرا شود تا تحویل نهایی و عملیاتی شدن سیستم تضمین گردد.

---

۲. معماری سیستم (سه‌لایه)

لایه توضیح مسیرها
لایه تعریف و حاکمیت ایجنت‌ها، قوانین، گردش‌های کار .claude/agents/، governance/، workflows/
لایه هسته‌ی اجرایی سرویس‌های پایتون، کتابخانه‌ها، کافکا src/، src/lib/، deployment/
لایه رابط کاربری و نظارت داشبورد واکنش‌گرا و API ui/

---

۳. قوانین طلایی (Golden Rules)

· Rule 01: ایجنت تصمیم نهایی نمی‌گیرد؛ کمیته‌ی انسانی تأیید یا رد می‌کند.
· Rule 02: تعاریف به زبان مارک‌داون (Claude-native) و کامپایلر آن‌ها را به ماشین‌خوان تبدیل می‌کند.
· Rule 03: هیچ اجرای Mock/ساختگی در سیستم مجاز نیست؛ همه چیز با سرویس‌های واقعی اجرا می‌شود.

---

۴. استخراج و یکپارچه‌سازی کدها (مراحل طی‌شده)

مرحله اقدام دستور اصلی
۱ کپی منبع اصلی از گوشی به source-main/AgentOS cp -r ...
۲ حذف پوشه‌های قدیمی src، ui، deployment، domain_pilots rm -rf
۳ کپی سرویس‌های هسته از فاز ۱ cp -r "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 01-08/..." src/core_services/
۴ کپی سرویس‌های دامنه (BL13, BL17) با اصلاح تودرتو cp -r "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 08-18/bl13_recommendation_plane_service_v2/bl13_recommendation_plane_service_v2" src/domain_services/recommendation_plane/
۵ کپی کنسول حکمرانی (BL19) cp -r "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 19-25/bl19_governance_console_service_v2_sso_rbac_np" src/governance_console/
۶ کپی فایل‌های استقرار (docker-compose و k8s) cp "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 01-08/docker-compose.yml" deployment/docker-compose.core.yml   cp -r "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 01-08/k8s" deployment/k8s
۷ کپی کتابخانه‌های بلوکی (BL01-08 و BL08-18) به src/lib/ cp "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 01-08/"*.py src/lib/   cp "source-main/AgentOS/PHASE 1/1-BLOCKS/BL 08-18/"*.py src/lib/
۸ کپی رابط کاربری (UI) از فاز ۲ و مسطح‌سازی tar -C "source-main/AgentOS/PHASE 2/Landing UI" -cf - . \| tar -xf - -C ui   سپس mv ui/ui/* ui/ و rmdir ui/ui
۹ کپی پایلوت‌های دامنه از فاز ۲ cp -r "source-main/AgentOS/PHASE 2/AACP_PHASE2_DOMAIN1_PILOT_FULL_v2" domain_pilots/ ...
۱۰ کپی SDK و مستندات شرکا از فاز ۱ (با tar برای جلوگیری از خطا) tar -C "source-main/AgentOS/PHASE 1" -cf - "AACP_PARTNER_SDK_..." \| tar -xf - -C . و تغییر نام
۱۱ پاک‌سازی و حذف پوشه‌های موقت rm -rf source-main phase1_files.txt phase2_files.txt

---

۵. ساختار نهایی ریپو (تعداد فایل‌ها: ۲۷۵)

```
AGENTS-OS/
├── .claude/                     (تعاریف ایجنت‌ها – دست‌نخورده)
├── governance/                  (قوانین و حاکمیت)
├── workflows/                   (گردش‌های کار)
├── committee/                   (کمیته‌ی اجرایی)
├── decisions/                   (لاگ تصمیمات)
├── identities/                  (ثبت هویت ایجنت‌ها)
├── src/                         (سرویس‌های هسته از فاز ۱)
│   ├── core_services/           (BL01-08)
│   ├── domain_services/         (BL13, BL17)
│   ├── governance_console/      (BL19)
│   └── lib/                     (کتابخانه‌های بلوکی)
├── ui/                          (رابط کاربری از فاز ۲ – مسطح‌شده)
│   ├── index.html, css/, js/, assets/, services/, ...
├── deployment/                  (فایل‌های استقرار)
│   ├── docker-compose.core.yml
│   └── k8s/
├── domain_pilots/               (پایلوت‌های دامنه از فاز ۲)
├── partner_sdk/                 (SDK شرکا از فاز ۱)
├── partner_sdk_spec/            (مشخصات SDK)
├── scripts/                     (اسکریپت‌های استقرار)
│   ├── fixed_deploy.sh
│   ├── full_deploy.sh
│   └── no_docker_deploy.sh
├── Makefile, CLAUDE.md, README.md, ...
└── (سایر فایل‌های مستندات)
```

---

۶. تعاریف ایجنت‌ها (.claude/agents/)

شامل ۱۱ ایجنت اصلی + ایجنت جدید presentation-assistant که در طول پروژه اضافه شد. هر ایجنت شامل Mission، Responsibilities، Authority Boundary و قوانین تصمیم‌گیری است.

---

۷. سرویس‌های هسته و موقعیت آن‌ها

بلوک سرویس مسیر
BL01-08 Agent Registry, Policy Plane, Permit Service, Audit Sink src/core_services/
BL13 Recommendation Plane src/domain_services/recommendation_plane/
BL17 Intent Gateway src/domain_services/intent_gateway/
BL19 Governance Console src/governance_console/
کتابخانه‌ها بلوک‌های ۱ تا ۱۸ src/lib/

---

۸. راه‌اندازی کافکا و زوکیپر (Native)

· مسیر: ~/kafka/kafka_2.13-3.4.0/
· فایل کانفیگ: config/zookeeper.properties (با dataDir=./zookeeper-data برای جلوگیری از خطای دسترسی)
· دستور راه‌اندازی در پس‌زمینه:
    bin/zookeeper-server-start.sh config/zookeeper.properties > /dev/null 2>&1 &
    sleep 5
    bin/kafka-server-start.sh config/server.properties > /dev/null 2>&1 &
    sleep 10
· ایجاد توپیک‌ها: کامپایلر خودکار توپیک‌های agent-*-inputs را ایجاد می‌کند. برای توپیک claude-agent-recommendations (بریج)، از دستور زیر استفاده می‌شود:
    bin/kafka-topics.sh --create --topic claude-agent-recommendations --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

---

۹. کامپایلر و بریج

· کامپایلر (src/infrastructure/agent_schema_compiler/compiler.py): فایل‌های .md را می‌خواند و توپیک‌های کافکا و اسکیماهای JSON تولید می‌کند.
· بریج (src/core_services/agent_bridge/bridge.py): به توپیک claude-agent-recommendations گوش می‌دهد و پیام‌های JSON را به توپیک‌های agent-*-inputs ارسال می‌کند.

---

۱۰. اسکریپت استقرار نهایی (scripts/fixed_deploy.sh)

این اسکریپت تمام سرویس‌ها، کافکا، کامپایلر و UI را به‌صورت خودکار و بدون داکر بالا می‌آورد.
دستور اجرا: ./scripts/fixed_deploy.sh

مراحل داخل اسکریپت:

1. راه‌اندازی زوکیپر و کافکا در پس‌زمینه.
2. اجرای سرویس‌های پایتون (main.py هر سرویس).
3. اجرای کامپایلر برای ایجاد توپیک‌ها.
4. اجرای سرور HTTP برای UI (پورت ۸۰۸۹).

---

۱۱. آزمون‌های عملیاتی (پس از اجرای اسکریپت)

آزمون روش نتیجه‌ی مورد انتظار
بررسی سلامت کافکا bin/kafka-topics.sh --list --bootstrap-server localhost:9092 نمایش لیست توپیک‌ها (شامل agent-*-inputs)
ارسال پیام تست echo '{"agent_id":"presentation-assistant","summary":"تست"}’ \| bin/kafka-console-producer.sh --broker-list localhost:9092 --topic claude-agent-recommendations بدون خطای LEADER_NOT_AVAILABLE
دریافت پیام در توپیک مقصد bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic agent-presentation-assistant-inputs --from-beginning --max-messages 1 نمایش JSON ارسال‌شده
بررسی UI باز کردن http://localhost:8089 در مرورگر نمایش داشبورد با تم‌های موجود
بررسی سرویس‌های پایتون ps aux \| grep python نمایش تمام فرآیندهای main.py

---

۱۲. کامیت و تگ نهایی

دستورات زیر برای ثبت تغییرات نهایی و ایجاد نسخه‌ی v1.0.0-rc2:

```bash
git add .
git commit -m "feat: Complete structural migration and source integration - 275 files"
git tag -a v1.0.0-rc2 -m "Release Candidate 2: Complete merge of Phase 1 & Phase 2 sources."
git push origin main
git push origin v1.0.0-rc2
```

---

۱۳. انتشار ریلیز (در گیت‌هاب)

پس از تگ، یک ریلیز با عنوان AgentOS v1.0.0-rc2 ایجاد کنید و یادداشت‌های انتشار را شامل تمام ویژگی‌ها و تغییرات کلیدی بنویسید.

---

۱۴. گام‌های تکمیلی (پس از عملیاتی‌سازی)

· رفع خطای Exit 127 کافکا: اگر در محیط WSL با خطای Exit 127 مواجه شدید، از اسکریپت scripts/no_docker_deploy.sh استفاده کنید که کافکا را به‌صورت مستقیم اجرا می‌کند.
· فعال‌سازی یادگیری (برای نسخه‌ی آینده): پیاده‌سازی سرویس Memory Refiner برای تحلیل تصمیمات انسانی و به‌روزرسانی پایگاه دانش ایجنت‌ها (در فاز v2.0.0).
· مهاجرت به محیط ابری: استفاده از فایل‌های k8s در deployment/k8s/ برای استقرار در کوبرنتیز.

---

۱۵. پیوست‌ها

· پیوست الف: فهرست کامل ۲۷۵ فایل (دستور find . -type f \| wc -l).
· پیوست ب: لیست تمام دستورات cp و tar استفاده‌شده در مهاجرت.
· پیوست ج: نقشه‌ی کامل بلوک‌ها (BL01-25) با توضیحات و مسیرهای فعلی.

---

پایان مستند گام آلفا
این مستند به‌عنوان مرجع نهایی برای تحویل سیستم AGENTS-OS در نظر گرفته شده است. پس از اجرای تمام مراحل و تأیید آزمون‌ها، سیستم آماده‌ی بهره‌برداری است. 🚀
