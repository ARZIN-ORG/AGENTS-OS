"""Locked constraints enforcement — Phase 1/2.

This module MUST be used by all services as a fail-fast guardrail.
"""

LOCKS = {
    "phase": "phase1",
    "no_autonomous_decisions": True,
    "human_in_the_loop_required": True,
    "voice_text_no_direct_publish": True,
    "aacp_only_operational_path": True,
    "deployment": "private_cloud_only",
}
