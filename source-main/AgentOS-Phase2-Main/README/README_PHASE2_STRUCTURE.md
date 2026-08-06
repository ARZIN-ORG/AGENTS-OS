# AgentOS — Phase-2 Main Bundle (Re-foldered)
این باندل برای این ساخته شده که «همه فایل‌ها بدون حذف» حفظ شوند، ولی یک ساختار Phase-2 قابل استفاده و قابل ارجاع هم داشته باشیم.

## اصل غیرقابل مذاکره
- هیچ فایلی حذف نشده است.
- کل Drop اصلی دقیقاً با همان ساختار اولیه در مسیر زیر نگه داشته شده است:
  - `99_Original_Drop/`

## فولدرهای اصلی (Phase-2)
- `01_UI/`
  - `core/` هسته UI (Bilingual Core + View Families)
  - `themes/` تم‌ها (Arzin / PedramFlow)
  - `views/` پکیج 33 ویو
  - `wired/` نسخه‌های wired (RealMode)
  - `services/` کانفیگ و اتصال UI به سرویس‌ها
- `02_ControlPlane/`
  - `Phase1_Blocks/` بلوک‌های BL-01..BL-08 (و پلاگین/وایرینگ‌ها)
- `05_Domain_Pilots/Phase2/`
  - پایلوت‌های دامنه‌های فاز ۲ و کانترکت‌ها/تصمیم انتخاب دامنه
- `06_Partner_SDK/` اسکلت SDK و Spec شریک
- `07_Governance_Docs/` Freeze / Entry Contract / External Notice

## چرا این ساختار؟
برای اینکه CTO بتواند سریعاً:
1) UI را جدا ببیند
2) Control Plane را جدا ببیند
3) Domain Pilotها را جدا ببیند
4) و در عین حال Drop اصلی هم برای دیباگ/trace موجود باشد.
