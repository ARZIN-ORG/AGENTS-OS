# 🧠 AGENTS-OS UI

## معماری
- **Core**: منطق اصلی (API, Auth, i18n, Router, Theme)
- **Views**: صفحات مجزا با کنترلرهای مستقل
- **Manifests**: پیکربندی ویوها (JSON)
- **Assets**: فونت‌ها و تصاویر
- **Themes**: تم‌های منطقه‌ای

## افزودن ویو جدید
1. یک فایل `{category}__{view-name}.json` در `manifests/views/` بسازید.
2. دو فایل `{view-name}.html` و `{view-name}.js` در `views/{category}/` ایجاد کنید.
3. در `view-registry.json` ویو را ثبت کنید.

## تغییر تم
1. فایل `core/theme-{name}.css` را ایجاد کنید.
2. در `core-theme.js` به `themeMap` اضافه کنید.
3. دکمه‌ی جدید در `index.html` اضافه کنید.

## اتصال به بک‌اند
1. `core/app.config.json` را ویرایش کنید.
2. `core-api.js` اصلاح شده است.

## توسعه‌ی محلی
```bash
python3 -m http.server 8089

