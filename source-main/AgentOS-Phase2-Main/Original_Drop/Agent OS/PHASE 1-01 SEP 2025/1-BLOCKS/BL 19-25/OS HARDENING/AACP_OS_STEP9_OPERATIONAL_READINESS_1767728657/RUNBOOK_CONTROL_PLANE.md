Runbook عملیاتی Control Plane — فاز ۱

سناریو ۱: Policy Plane Down
وضعیت: Fail-Closed
اقدام: توقف صدور Permit، ادامه Recommendation
Escalation: Governance + CTO
اقدام اصلاحی: بازیابی Policy Store از Snapshot معتبر

سناریو ۲: Permit Service Down
وضعیت: Fail-Closed
اقدام: Block همه publishهای عملیاتی
Escalation: Ops فوری
یادداشت: هیچ Bypass مجاز نیست

سناریو ۳: Audit Sink Lag
وضعیت: Fail-Closed
اقدام: توقف Execution
اقدام اصلاحی: افزایش Partition / IO

سناریو ۴: Kafka Partition Failure
وضعیت: Degraded but Safe
اقدام: ادامه Recommendation، توقف Execution
