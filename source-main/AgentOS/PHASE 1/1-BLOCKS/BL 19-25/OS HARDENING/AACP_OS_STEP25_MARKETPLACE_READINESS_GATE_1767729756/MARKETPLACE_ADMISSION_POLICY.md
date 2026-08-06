Marketplace Admission Policy (Phase 2 Gate)

Core idea:
Marketplace is only the distribution surface.
The OS Control Plane is the governor.

Admission levels:
L0: Internal-only agent
L1: Partner sandbox (read-only + shadow)
L2: Partner recommendation (limited scope)
L3: Partner recommendation (multi-scope) — requires governance upgrade

Mandatory for any admission > L0:
- Registry identity verified
- Signed messages + rotation
- Audit envelope complete
- Policy scope bound
- Channel bound
- Kill-switch tested
- Test harness pass (chaos + fail-closed)