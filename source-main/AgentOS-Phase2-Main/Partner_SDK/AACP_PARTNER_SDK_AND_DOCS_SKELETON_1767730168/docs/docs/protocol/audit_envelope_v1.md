# Audit Envelope v1 (Mandatory)
فیلدهای اجباری: trace_id, message_id, schema_version, timestamp_ms, producer_id, consumer_id, channel,
policy_scope, signature_alg, signature, chain_hash, permit_status, audit_version.
کمبود هر فیلد = Reject.
