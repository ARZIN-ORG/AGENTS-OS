AgentOS UI Core + View Families (Final v1)
Generated: 2026-01-07T15:59:07.751308Z

- UI Core: router, RBAC hooks, i18n (fa/en), RTL/LTR, brand themes (arzin/pedramflow)
- View Families: OS, Infra, Domain, Interaction (33 views)
- Real wiring targets: BL-06/07/08/17/19 via /api/bl06 ... /api/bl19
- No mocks: errors are surfaced, no fake data.

Run:
  python -m http.server 8080
Proxy (nginx):
  /api/bl06 -> BL-06
  /api/bl07 -> BL-07
  /api/bl08 -> BL-08
  /api/bl17 -> BL-17
  /api/bl19 -> BL-19
