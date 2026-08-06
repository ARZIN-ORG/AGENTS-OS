GameDay — سناریوهای تمرین عملیاتی

سناریو A: Publish بدون Permit
انتظار: Reject + DLQ + Audit

سناریو B: Policy Drift
انتظار: Block Execution + Alert Governance

سناریو C: Audit Sink Lag
انتظار: Fail-Closed Execution

سناریو D: Kafka Partition Loss
انتظار: Recommendation ادامه، Execution متوقف

سناریو E: Replay Attack
انتظار: Signature/Nonce Reject
