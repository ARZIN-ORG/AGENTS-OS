این سرویس با FastAPI اجرا می‌شود و OpenAPI را به‌صورت خودکار روی /docs تولید می‌کند.
Endpointهای کلیدی:
- GET /health
- POST /v1/audit/records
- GET /v1/audit/records/by-trace/{trace_id}
- GET /v1/audit/records/by-message/{message_id}
