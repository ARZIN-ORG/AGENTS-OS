# BL-07 — Policy Plane Service (Phase 1 / Private Cloud) — Architecture v1
شناسه: ARZIN-AOS-BL07-POLICY-ARCH-v1.0  
دامنه: فاز ۱ سیستم‌عامل ایجنت‌ها (Agent OS)  
هدف: Policy-as-Code سرویس‌محور با نسخه‌بندی، انتشار کنترل‌شده، و Audit تغییرات؛ خروجی فقط برای Observe/Recommend در فاز ۱.

این سرویس جزء Control Plane است. تصمیم Allow/Deny پیام در Data Plane و توسط Interceptor/SDK enforce می‌شود. Policy Plane مرجع Truth برای سیاست‌ها و نسخه‌ها است و خروجی «effective policy» را برای hot path فراهم می‌کند.

## ۱) قیود قفل‌شده و enforce
این سرویس باید تغییر سیاستی که منجر به decision_class خارج از observe/recommend شود را Reject کند.  
این سرویس باید مالکیت و تفکیک نقش را پشتیبانی کند و تغییرات را audit کند.  
استقرار صرفاً Private Cloud است و وابستگی بیرونی ندارد.  
انتشار سیاست باید کنترل‌شده باشد و rollback قابل انجام باشد.

## ۲) مسئولیت‌ها
Policy Definition: ذخیره تعریف policy به‌صورت نسخه‌دار.  
Policy Publish: فعال‌سازی یک نسخه برای یک scope مشخص.  
Policy Query: ارائه effective policy برای Agent/Channel/Topic.  
Audit: ثبت تمام تغییرات سیاست و انتشار.

## ۳) مدل سیاست (Phase 1)
Policy شامل:
- policy_id (immutable id)
- version (integer)
- status (draft/active/deprecated)
- scope: agent_class, agent_id (optional), channel_id, topic rules
- constraints: تصمیم فقط observe/recommend، محدودیت‌های پیام (size, ttl bounds), نیازمندی‌های امنیتی (signature_required=true)
Policy Engine در فاز ۱ عمداً ساده است و فقط constraintهای ضروری را enforce می‌کند.

## ۴) DoD برای CTO سخت‌گیر
ایجاد policy draft + validate سخت‌گیر.  
publish فقط با version و scope مشخص و audit.  
effective-policy endpoint برای Interceptor قابل cache باشد و پاسخ deterministic بدهد.  
rollback به نسخه قبلی عملی باشد و audit شود.  
هیچ مسیری برای execute یا bypass ایجاد نشود.
