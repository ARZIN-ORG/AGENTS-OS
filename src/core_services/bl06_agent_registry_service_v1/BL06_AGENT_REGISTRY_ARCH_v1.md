# BL-06 — Agent Registry Service (Phase 1 / Private Cloud) — Architecture v1
شناسه: ARZIN-AOS-BL06-REGISTRY-ARCH-v1.0  
دامنه: فاز ۱ سیستم‌عامل ایجنت‌ها (Agent OS)  
هدف: تبدیل Registry از «فایل/کد» به «سرویس حاکمیتی» با کنترل نسخه، وضعیت، و allowlist کانال/تاپیک.

این سرویس جزئی از Control Plane است و مسئول «هویت، وضعیت و دامنه مجاز Agent» است. Data Plane همچنان در Interceptor/SDK enforce می‌شود و سرویس Registry مرجع Truth برای allowlistها است.

## ۱) قیود قفل‌شده و نحوه enforce در این سرویس
این سرویس باید با قیود قفل‌شده فاز ۱ سازگار باشد و هر ثبت/به‌روزرسانی که آن‌ها را نقض کند باید Reject شود.  
در فاز ۱ و فاز ۲ هیچ Agent اجازه Decision Execution ندارد و تصمیم‌گیری اجرایی ممنوع است.  
این سرویس فقط دامنه Observe/Recommend را ثبت می‌کند و هر Decision Class خارج از این دامنه را رد می‌کند.  
استقرار فقط Private Cloud است و هیچ Discovery خارجی یا وابستگی SaaS در طراحی وجود ندارد.  
معماری چندکاناله AACP قفل است و Registry باید allowlist کانال و تاپیک را به‌صورت صریح نگهداری کند.

## ۲) مسئولیت‌ها
این سرویس مرجع ثبت و مدیریت وضعیت Agent است.  
این سرویس مالک چرخه عمر Agent است و اجازه می‌دهد Agent فعال، معلق، یا لغو شود.  
این سرویس allowlist کانال/تاپیک و کلاس‌های مجاز خروجی (observe/recommend) را نگهداری می‌کند.  
این سرویس به‌صورت ذاتی Audit Trail تغییرات را نگهداری می‌کند.

## ۳) خارج از دامنه
این سرویس پیام‌رسانی AACP را اجرا نمی‌کند.  
این سرویس تصمیم Allow/Deny برای هر پیام را صادر نمی‌کند.  
این سرویس به پیام‌های Kafka دست نمی‌زند و فقط Control Plane است.

## ۴) مدل داده (حداقلی و قابل توسعه)
Agent دارای شناسه یکتا، کلاس، نسخه، وضعیت، دامنه کانال/تاپیک مجاز، و metadata است.  
هر تغییر Agent یک رکورد Audit می‌سازد تا بازسازی تاریخچه ممکن باشد.

## ۵) رابط‌ها
این سرویس API داخلی دارد و برای Interceptor/SDK مصرف می‌شود.  
برای مسیر سریع (hot path) باید caching سمت Interceptor انجام شود تا latency اضافه نشود.  
سرویس Registry باید برای burstهای read-heavy آماده باشد و writeها محدود و کنترل‌شده هستند.

## ۶) HA و state
این سرویس stateful است و باید روی پایگاه داده رابطه‌ای در Private Cloud اجرا شود.  
برای فاز ۱، Postgres مرجع است و در حالت توسعه SQLite مجاز است.  
HA در سطح سرویس و DB باید با استاندارد Private Cloud شما انجام شود.

## ۷) تعریف Done (DoD) برای CTO سخت‌گیر
ثبت Agent با validate سخت‌گیر و Reject برای هر نقض قفل‌های فاز ۱ انجام شود.  
Update وضعیت و allowlist با version bump و audit ثبت شود.  
Read مسیرها سریع، قابل cache، و قابل استفاده برای Interceptor باشد.  
تمام endpoints با trace_id قابل لاگ باشند و خطاها deterministic باشند.  
هیچ endpointی امکان ثبت permission برای execute یا bypass فراهم نکند.
