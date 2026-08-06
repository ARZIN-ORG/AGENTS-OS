# Intent Interpretation Agent - Interaction Layer (Mandatory)
# Role: Translate Voice/Text input into structured Intent (proposal) for human review.
# IMPORTANT: Never publishes operational messages directly. Produces "IntentDraft".
# Enforces: MFA asserted identity must be provided by upstream (not here).

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, List


@dataclass(frozen=True)
class ActorIdentity:
    actor_id: str
    actor_role: str
    mfa_assured: bool


@dataclass(frozen=True)
class IntentDraft:
    intent_id: str
    actor_id: str
    channel: str  # "voice" | "text"
    raw_input: str
    normalized_intent: Dict[str, Any]
    requires_human_confirmation: bool
    confidence: float
    notes: List[str]


class IntentInterpretationAgent:
    def interpret(self, identity: ActorIdentity, raw_input: str, channel: str) -> IntentDraft:
        if not identity.mfa_assured:
            # Fail-closed. Upstream must assert MFA.
            return IntentDraft(
                intent_id="INTENT-REJECTED",
                actor_id=identity.actor_id,
                channel=channel,
                raw_input=raw_input,
                normalized_intent={},
                requires_human_confirmation=True,
                confidence=0.0,
                notes=["MFA not assured. Reject intent draft."],
            )

        if not raw_input or not raw_input.strip():
            return IntentDraft(
                intent_id="INTENT-EMPTY",
                actor_id=identity.actor_id,
                channel=channel,
                raw_input=raw_input,
                normalized_intent={},
                requires_human_confirmation=True,
                confidence=0.0,
                notes=["Empty input."],
            )

        # Minimal, auditable normalization (no hidden magic).
        # Real NLP can plug in later, but output must remain reviewable by human.
        normalized = {
            "type": "MANAGEMENT_REQUEST",
            "requested_action": "GENERATE_REPORT",
            "parameters": {"scope": "system", "window": "24h"},
        }

        return IntentDraft(
            intent_id=f"INTENT-{int(time.time())}",
            actor_id=identity.actor_id,
            channel=channel,
            raw_input=raw_input,
            normalized_intent=normalized,
            requires_human_confirmation=True,
            confidence=0.62,
            notes=["Draft only. Must be reviewed/edited/approved by human."],
        )
