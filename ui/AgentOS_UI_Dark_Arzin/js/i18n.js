// Minimal, dependency-free i18n for AgentOS UI (Phase-1 friendly).
// - No runtime fetch, no build step.
// - Supports fa (rtl) and en (ltr).
// - Translates nodes marked with [data-i18n] and [data-i18n-placeholder].

const DICT = {
  en: {
    "app.title": "AgentOS Governance Console",
    "ui.lang.en": "EN",
    "ui.lang.fa": "FA",
    "ui.lang.toggle": "Language",
    "nav.overview": "Overview",
    "nav.control": "Control Plane",
    "nav.data": "Data Plane",
    "nav.rules": "Locked Rules",
    "page.overview": "Governance Console",
    "page.agents": "Agents",
    "page.policy": "Policy Plane",
    "page.permit": "Permit Service",
    "page.audit": "Audit & Trace",
    "page.channels": "Channel Manager",
    "page.partners": "External Partners",
    "page.kpis": "KPI / KRI",
    "status.ok": "OK",
    "status.watch": "WATCH",
    "status.fail": "FAIL",
    "ui.search": "Search…",
    "ui.refresh": "Refresh",
    "ui.export": "Export",
    "ui.filter": "Filter",
    "ui.approve": "Approve",
    "ui.reject": "Reject",
    "ui.view": "View",
  },
  fa: {
    "app.title": "کنسول حاکمیتی سیستم‌عامل ایجنت‌ها",
    "ui.lang.en": "EN",
    "ui.lang.fa": "FA",
    "ui.lang.toggle": "زبان",
    "nav.overview": "نمای کلی",
    "nav.control": "کنترل‌پلین",
    "nav.data": "دیتاپلین",
    "nav.rules": "قفل‌ها",
    "page.overview": "کنسول حاکمیتی",
    "page.agents": "ایجنت‌ها",
    "page.policy": "پلین سیاست‌ها",
    "page.permit": "سرویس مجوز",
    "page.audit": "ممیزی و رهگیری",
    "page.channels": "مدیریت کانال",
    "page.partners": "شرکای بیرونی",
    "page.kpis": "شاخص‌ها (KPI/KRI)",
    "status.ok": "تأیید",
    "status.watch": "پایش",
    "status.fail": "رد",
    "ui.search": "جستجو…",
    "ui.refresh": "به‌روزرسانی",
    "ui.export": "خروجی",
    "ui.filter": "فیلتر",
    "ui.approve": "تأیید",
    "ui.reject": "رد",
    "ui.view": "مشاهده",
  }
};

const STORAGE_KEY = "agentos.lang";

export function getLang() {
  const raw = (localStorage.getItem(STORAGE_KEY) || "").trim().toLowerCase();
  return raw === "fa" ? "fa" : "en";
}

export function setLang(lang) {
  const v = (lang === "fa") ? "fa" : "en";
  localStorage.setItem(STORAGE_KEY, v);
  applyLang(v);
}

export function t(key) {
  const lang = getLang();
  return (DICT[lang] && DICT[lang][key]) || (DICT.en && DICT.en[key]) || key;
}

export function applyLang(lang) {
  const l = (lang === "fa") ? "fa" : "en";
  const dir = (l === "fa") ? "rtl" : "ltr";

  document.documentElement.setAttribute("lang", l);
  document.documentElement.setAttribute("dir", dir);
  document.title = t("app.title");

  // translate text nodes
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.getAttribute("data-i18n");
    if (!key) return;
    el.textContent = t(key);
  });

  // translate placeholders
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (!key) return;
    el.setAttribute("placeholder", t(key));
  });

  // update toggle label
  const btn = document.getElementById("langToggle");
  if (btn) {
    btn.setAttribute("aria-label", t("ui.lang.toggle"));
    btn.textContent = (l === "fa") ? t("ui.lang.en") : t("ui.lang.fa");
  }
}

export function initI18n() {
  // Ensure deterministic startup
  applyLang(getLang());

  const btn = document.getElementById("langToggle");
  if (btn) {
    btn.addEventListener("click", () => {
      setLang(getLang() === "fa" ? "en" : "fa");
    });
  }
}
