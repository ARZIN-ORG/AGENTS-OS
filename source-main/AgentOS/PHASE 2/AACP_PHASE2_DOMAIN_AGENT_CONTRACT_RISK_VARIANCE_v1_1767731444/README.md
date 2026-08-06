# Official Agent Contract — Operational Risk & Variance Advisor (v1.0.0)

این بسته «قرارداد رسمی» برای رجیستری و Policy Plane است.
قفل‌های فاز ۱ و ۲ رعایت شده‌اند:
- فقط RECOMMENDATION
- Human Approval اجباری
- Fail-Closed برای Audit/Signature/Policy/Channel
- هیچ مسیر Execute در خود Agent/SDK تعریف نشده است

فایل‌ها:
- agent_contract.yaml : تعریف رسمی AgentContract برای Registry
- policy_binding.yaml : نمونه Binding برای Policy Plane (Scope/Topics/Constraints)

نکته اجرایی:
اگر هر بند از guardrails نقض شود، interceptor/kafka-manager باید پیام را Reject + DLQ کند.
