# aacp_test_harness_phase1.py
# -*- coding: utf-8 -*-
"""
Test Harness (Phase 1) — strict fail cases

Run:
  python -m unittest aacp_test_harness_phase1.py
"""

from __future__ import annotations

import unittest

from aacp_audit_envelope_v1 import AACPAuditEnvelopeV1, AgentType, DecisionClass, SignatureAlg, compute_chain_hash
from aacp_message_schema_v1 import AACPMessage, Metadata, Routing, Security, Payload
from aacp_kafka_interceptor import validate_message_phase1
from aacp_registry_policy_min import InMemoryAgentRegistry, InMemoryPolicyResolver


def make_message(*, decision: DecisionClass = DecisionClass.observe, chain_ok: bool = True) -> AACPMessage:
    payload_dict = {"x": 1}

    env_base = {
        "agent_id": "agent-1",
        "agent_type": AgentType.observe,
        "agent_version": "1.0.0",
        "channel_id": "ch-1",
        "topic": "PAYMENT_INITIATED",
        "flow_id": "flow-1",
        "policy_id": "pol-1",
        "policy_version": "1",
        "decision_class": decision,
        "signature": "QUJDRA==",  # base64("ABCD") placeholder
        "signature_alg": SignatureAlg.Ed25519,
        "key_id": "key-1",
        "prev_chain_hash": None,
    }

    # Create envelope with temporary chain_hash to compute the real one.
    temp = dict(env_base)
    temp["chain_hash"] = "0" * 64
    env_temp = AACPAuditEnvelopeV1(**temp)

    env_wo = env_temp.dict()
    env_wo.pop("chain_hash", None)

    correct_chain = compute_chain_hash(envelope_without_chain=env_wo, payload=payload_dict, prev_chain_hash=None)
    final_chain = correct_chain if chain_ok else ("f" * 64)

    env_base["chain_hash"] = final_chain
    env = AACPAuditEnvelopeV1(**env_base)

    msg = AACPMessage(
        metadata=Metadata(schema_version="1.0", source="unit-test"),
        routing=Routing(channel_id="ch-1", topic="PAYMENT_INITIATED", flow_id="flow-1"),
        security=Security(signature=env.signature, signature_alg=env.signature_alg.value, key_id=env.key_id),
        payload=Payload(data=payload_dict),
        audit=env,
    )
    return msg


class TestPhase1Harness(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = InMemoryAgentRegistry(agents={"agent-1": {"name": "t"}})
        self.policies = InMemoryPolicyResolver(policies={"pol-1": {"1": {"active": True}}})

    def test_execute_forbidden(self) -> None:
        msg = make_message(decision=DecisionClass.execute)
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=self.registry,
            policy_resolver=self.policies,
            signature_verifier=lambda env, payload: True,
        )
        self.assertFalse(ok)
        self.assertEqual(code.value, "EXECUTE_FORBIDDEN")

    def test_chain_hash_mismatch(self) -> None:
        msg = make_message(chain_ok=False)
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=self.registry,
            policy_resolver=self.policies,
            signature_verifier=lambda env, payload: True,
        )
        self.assertFalse(ok)
        self.assertEqual(code.value, "CHAIN_HASH_MISMATCH")

    def test_signature_invalid(self) -> None:
        msg = make_message()
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=self.registry,
            policy_resolver=self.policies,
            signature_verifier=lambda env, payload: False,
        )
        self.assertFalse(ok)
        self.assertEqual(code.value, "SIGNATURE_INVALID")

    def test_agent_not_registered(self) -> None:
        msg = make_message()
        reg = InMemoryAgentRegistry(agents={})
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=reg,
            policy_resolver=self.policies,
            signature_verifier=lambda env, payload: True,
        )
        self.assertFalse(ok)
        self.assertEqual(code.value, "AGENT_NOT_REGISTERED")

    def test_policy_mismatch(self) -> None:
        msg = make_message()
        pol = InMemoryPolicyResolver(policies={"pol-1": {"2": {"active": True}}})
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=self.registry,
            policy_resolver=pol,
            signature_verifier=lambda env, payload: True,
        )
        self.assertFalse(ok)
        self.assertEqual(code.value, "POLICY_MISMATCH")

    def test_ok(self) -> None:
        msg = make_message()
        ok, code, _ = validate_message_phase1(
            msg=msg,
            agent_registry=self.registry,
            policy_resolver=self.policies,
            signature_verifier=lambda env, payload: True,
        )
        self.assertTrue(ok)
        self.assertIsNone(code)


if __name__ == "__main__":
    unittest.main()
