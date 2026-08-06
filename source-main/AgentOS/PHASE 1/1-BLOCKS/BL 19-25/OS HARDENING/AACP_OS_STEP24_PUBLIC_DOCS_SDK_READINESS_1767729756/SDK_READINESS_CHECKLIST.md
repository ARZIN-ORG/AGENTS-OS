SDK Readiness Checklist

Required:
- Message codec library
- Audit envelope builder
- Signature helper (verify/sign)
- Channel config loader
- Test harness client (shadow mode)
- Error taxonomy + DLQ schema
- Version compatibility matrix

Rules:
- SDK cannot provide any execute helper
- SDK must fail-closed on missing audit fields