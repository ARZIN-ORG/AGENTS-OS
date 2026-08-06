AACP Plug-in BL-08 (Phase 1)

Files:
- aacp_kafka_interceptor_PLUG_BL08.py
- aacp_kafka_manager_PLUG_BL08.py

What you get:
- Existing AACPMessage v1 continues to work.
- Enforcement is upgraded to BL-01..BL-08 via adapter/wrapper.
- Reject -> DLQ is always executed.
- Signature verification is mandatory (KeyStore).
- Registry + Policy allow-lists enforce channel/topic/decision_class constraints.

What you still must provide in Private Cloud:
- channels.json (ChannelManager)
- registry.json  (Agent allow-list: channels/topics per agent)
- policies.json  (Policy allow-list: decision_classes/channels/topics)
- keystore.json  (key_id -> PEM public keys)

Operational note:
- For Audit immutability: configure Kafka retention + ACLs + (optionally) WORM store.
