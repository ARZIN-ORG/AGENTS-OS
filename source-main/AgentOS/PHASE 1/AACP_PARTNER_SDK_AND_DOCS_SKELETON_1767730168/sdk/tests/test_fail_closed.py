import pytest
from aacp_partner_sdk.audit import AuditEnvelopeBuilder
from aacp_partner_sdk.shadow_client import ShadowClient
from aacp_partner_sdk.types import PolicyScope, ChannelBinding

def test_missing_audit_fields_fails():
    with pytest.raises(Exception):
        AuditEnvelopeBuilder.build({"trace_id":"x"})

def test_execute_intent_forbidden():
    c = ShadowClient(scope=PolicyScope("sc1"), channel=ChannelBinding("aacp.partner.canary"))
    msg = {"schema_version":"1.0", "audit": {
        "trace_id":"t","message_id":"m","schema_version":"1.0","timestamp_ms":1,
        "producer_id":"p","consumer_id":"c","channel":"x","policy_scope":"s",
        "signature_alg":"rsa","signature":"sig","chain_hash":"h","permit_status":"DENIED","audit_version":"1",
    }, "intent":"EXECUTE"}
    with pytest.raises(Exception):
        c.prepare(msg)
