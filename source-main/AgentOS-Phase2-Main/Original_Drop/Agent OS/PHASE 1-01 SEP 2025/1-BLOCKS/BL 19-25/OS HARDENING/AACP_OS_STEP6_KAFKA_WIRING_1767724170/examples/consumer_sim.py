from __future__ import annotations

from libs.aacp_kafka.kafka_io import AACPEnv, make_interceptor

def main():
    env = AACPEnv.from_env()
    interceptor = make_interceptor(env)

    # In real consume, headers/payload come from Kafka message
    headers = {
        "x-aacp-trace-id": "trc-1",
        "x-aacp-event-id": "evt-1",
        "x-aacp-producer-id": "agent.reco",
        "x-aacp-consumer-id": "svc.domain",
        "x-aacp-channel-id": "channel::default",
        "x-aacp-topic": "aacp.recommendations",
        "x-aacp-schema-id": "REC-001",
        "x-aacp-schema-version": "1",
        "x-aacp-policy-id": "POLICY-DEFAULT",
        "x-aacp-policy-version": "1",
        "x-aacp-permit-id": "PERMIT-DEFAULT",
        "x-aacp-intent-id": "INTENT-123",
        "x-aacp-sig-alg": "HMAC-SHA256-DEV",
        "x-aacp-signature": "deadbeef",
    }
    payload = {"type": "RECOMMENDATION", "body": {"note": "advisory only"}, "ts": 123}
    interceptor.guard_consume(headers, payload)
    print("CONSUME_ALLOWED")

if __name__ == "__main__":
    main()
