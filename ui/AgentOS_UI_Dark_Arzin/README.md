# AgentOS Governance Console UI (Dark (Arzin))

This is a static, dependency-free UI bundle intended for Phase‑1 governance operations.
It is safe for private-cloud deployment (no external CDN, no tracking, no remote calls).

## What’s included
- `index.html` + `css/` + `js/` + `assets/`
- Built-in language toggle: **FA (rtl)** ⇄ **EN (ltr)**
- Theme-specific visuals (dark/light) while keeping one unified interaction model

## How to run locally
Open `index.html` in a browser, or serve the folder with a static server.

## i18n / RTL-LTR
Language selection is stored in `localStorage` key `agentos.lang`.
- `fa` => `dir=rtl`
- `en` => `dir=ltr`

## Notes for production
- Put behind SSO / mTLS / reverse proxy (as per Control Plane hardening steps).
- Keep the UI read-only by default; actions must flow through Intent→Confirm→Permit→AACP.

## Version
- UI Bundle: v1.1 (bilingual + rtl/ltr)
