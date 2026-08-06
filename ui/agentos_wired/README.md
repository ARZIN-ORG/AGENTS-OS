# AgentOS Governance Console — Wired (Phase-1)

این بسته، همان UI نهایی شماست با «سیم‌کشی واقعی» به سرویس‌ها، و حذف مسیرهای mock در حالت `mode=real`.

## اجزای بسته

- `ui/` : استاتیک SPA (دو زبانه RTL/LTR) با قابلیت `mode: mock|real`.
- `services/governance-console-api/` : BFF سبک (FastAPI) برای اتصال UI به سرویس‌های BL و SSO/RBAC.

## اصل قفل‌شده

- هیچ Voice/Text مستقیماً AACP publish نمی‌کند.
- UI فقط Intent می‌سازد/نمایش می‌دهد و برای اجرا، Permit لازم است.
- اجرای عملیاتی فقط از مسیر AACP + Permit + Audit + Trace.

## اجرای محلی سریع

### 1) اجرای BFF

```bash
cd services/governance-console-api
python -m venv .venv && source .venv/bin/activate
pip install -r <(python -c "import tomllib;print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))")
uvicorn app.main:app --reload --port 8080
```

### 2) اجرای UI

- `ui/index.html` را با هر static server اجرا کنید.
- در `ui/index.html` مقدار `window.__AGENTOS_CONFIG__` را به شکل زیر تنظیم کنید:

```js
window.__AGENTOS_CONFIG__ = {
  mode: "real",
  apiBaseUrl: "http://localhost:8080",
  requestTimeoutMs: 8000
}
```

## اتصال به سرویس‌های BL

BFF این متغیرهای محیطی را می‌گیرد:

- `BL06_REGISTRY_URL` (Agent Registry)
- `BL07_POLICY_URL` (Policy Plane)
- `BL08_PERMIT_URL` (Permit Service)
- `BL19_GOVCONSOLE_URL` (اختیاری، برای سرویس‌های مکمل)
- `BL17_INTENT_URL` (Intent Gateway)

اگر هرکدام ست نشده باشد، BFF با پیام واضح `502 upstream_unreachable` برمی‌گرداند (Fail-fast).

## Auth/RBAC/SSO

- BFF انتظار `Authorization: Bearer <JWT>` دارد.
- اعتبارسنجی کلید با `JWT_JWKS_URL` یا `JWT_PUBLIC_KEY_PEM`.
- نقش‌ها از claim استاندارد `roles` خوانده می‌شوند.

## وضعیت حذف Mock

- در `mode=mock`: UI روی داده‌های نمونه بالا می‌آید.
- در `mode=real`: UI فقط از BFF می‌خواند و اگر Backend نرسد، خطا را نمایش می‌دهد.

