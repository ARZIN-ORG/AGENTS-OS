# Runbook — Stateful BL-13/BL-17 + Audit wiring

## Local smoke (docker-compose)
1) Place folders:
   - bl13_recommendation_plane_service_v2
   - bl17_intent_gateway_service_v2
   alongside docker-compose.yaml
2) Run:
   docker compose up -d
3) Check:
   - BL-13: http://localhost:8082/health
   - BL-17: http://localhost:8083/health

## Core acceptance criteria
- Restart BL-13 / BL-17 and confirm suggestions/intents persist (DB).
- Accepting a suggestion fails if Audit Sink is down (strict governance mode).
- No operational publish is performed on Permit deny (fail-closed).

## Private cloud notes
- Replace embedded DB creds with secrets manager.
- Run Postgres as HA (Patroni / managed PG) — single replica only for dev.
- Add NetworkPolicy: only BL-13/BL-17 -> Permit/Audit/Policy/Registry, and BL-17 -> BL-13.
