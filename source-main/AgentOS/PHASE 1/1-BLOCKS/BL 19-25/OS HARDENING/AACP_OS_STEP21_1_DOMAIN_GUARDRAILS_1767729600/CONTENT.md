
This document defines hard guardrails for Domain Agents in Phase 2.

Rules:
- Domain agents may only generate recommendations.
- No write access to execution channels.
- All outputs require Permit review.
- Confidence, uncertainty, and data lineage are mandatory.

Violation = automatic rejection + audit flag.
