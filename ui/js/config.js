// پیکربندی پویا که از فایل config.json در ریشه‌ی ui/ خوانده می‌شود
// این فایل به‌صورت داینامیک توسط سرور سرو می‌شود و می‌تواند در محیط‌های مختلف (محلی، ابری) تغییر کند.

export async function getConfig() {
  try {
    const response = await fetch('/config.json');
    if (!response.ok) throw new Error('Failed to load config');
    const c = await response.json();

    // اگر یک شیء window.__AGENTOS_CONFIG__ موجود باشد (برای سازگاری با نسخه‌های قبلی)، اولویت با آن است.
    const windowCfg = (typeof window !== 'undefined' && window.__AGENTOS_CONFIG__) ? window.__AGENTOS_CONFIG__ : {};
    
    const merged = { ...c, ...windowCfg };
    const apiBaseUrl = (merged.apiBaseUrl || '').toString().replace(/\/$/, '');

    return {
      mode: (merged.mode || 'real').toString(),
      apiBaseUrl,
      requestTimeoutMs: Number(merged.requestTimeoutMs || 8000),
      auth: {
        enabled: merged.auth && typeof merged.auth.enabled === 'boolean' ? merged.auth.enabled : true,
      },
    };
  } catch (e) {
    // حالت بازگشتی در صورت عدم دسترسی به فایل پیکربندی (برای توسعه)
    console.warn('⚠️ Config file not found. Falling back to defaults.');
    return {
      mode: 'real',
      apiBaseUrl: 'http://localhost:8090',
      requestTimeoutMs: 8000,
      auth: { enabled: false }
    };
  }
}

export function isRealMode(){
  return true; // حالت واقعی همیشه فعال است
}
