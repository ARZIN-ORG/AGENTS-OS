from __future__ import annotations

import os
from libs.aacp_kafka.kafka_io import AACPEnv, build_headers, sign_payload_dev, make_interceptor

def main():
    env = AACPEnv.from_env()
    interceptor = make_interceptor(env)

    payload = {"type": "RECOMMENDATION", "body": {"note": "advisory only"}, "ts": 123}
    headers = build_headers(
        topic="aacp.recommendations",
        producer_id="agent.reco",
        consumer_id="broker.kafka",
        schema_id="REC-001",
        schema_version="1",
        policy_id="POLICY-DEFAULT",
        policy_version="1",
        permit_id="PERMIT-PENDING",
        intent_id="INTENT-123",
    )
    headers = sign_payload_dev(headers, payload, env.dev_secret)

    # Simulate the human approval flag coming from Governance Console final approval
    out_headers, out_payload = interceptor.guard_publish(headers, payload, human_approved=True)
    print("PUBLISH_ALLOWED", out_headers["x-aacp-trace-id"])

if __name__ == "__main__":
    main()
