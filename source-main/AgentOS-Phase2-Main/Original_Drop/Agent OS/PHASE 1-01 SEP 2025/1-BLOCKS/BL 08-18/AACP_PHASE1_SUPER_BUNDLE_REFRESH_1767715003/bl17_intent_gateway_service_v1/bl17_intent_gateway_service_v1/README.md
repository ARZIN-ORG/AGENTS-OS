# BL-17 — Omni-Channel Intent Gateway (Phase 1)

Purpose:
- Accept **Voice/Text** managerial/user inputs.
- Convert to a structured **Intent Draft**.
- Force **human review/edit + final approval**.
- After approval: request execution via **BL-08 Permit** and publish via AACP Event Fabric (Kafka manager plugin), **never directly from Voice/Text**.

Also exposes a thin proxy to BL-13 Recommendation Plane for listing/reviewing suggestions:
- BL-13 stores suggestions and handles ACCEPT -> Permit -> (optional) publish.
- BL-17 is the UI/API-facing control point for humans.

Locked rules enforced:
- No AI veto after human final approval.
- Fail-closed on Permit/Audit path errors.
- Voice/Text never publish operational messages directly.

Phase-1 notes:
- Voice endpoint is a stub (expects text transcript). Real ASR integration is outside this package.
- Intent extraction is deterministic and rule-based placeholder.
