# BL-13 — Recommendation Plane (Phase 1)

This service implements the **Smart Suggestion** plane for Agent OS Phase-1.

Locked rules enforced:
- Suggestions are **non-executable** artifacts.
- Execution happens **only** after human acceptance and **only** via AACP path:
  Permit + Audit + Trace.
- No direct operational publish from Voice/Text UI.
- Fail-closed: if Permit/Audit path is unavailable, no execution is triggered.

What this service does:
1) Create/store suggestions (recommendations).
2) Present suggestions for review (API for UI/Voice/Text clients).
3) Accept/reject/modify suggestions.
4) On accept: builds an Execution Request and submits to Permit Service, then (optionally)
   publishes the approved request to the Event Fabric via the existing AACP Kafka wiring.

Phase-1 minimal: no learning, no autonomy, no federation.
