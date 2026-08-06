#!/bin/bash
echo "🚀 اجرای سیستم بدون کانتینر (مستقیماً روی پایتون و کافکا)..."

# تنظیم آدرس کافکا
export KAFKA_BROKER="localhost:9092"

# ۱. راه‌اندازی زوکیپر و کافکا در پس‌زمینه
cd ~/kafka/kafka_2.13-3.4.0
bin/zookeeper-server-start.sh config/zookeeper.properties &
sleep 5
bin/kafka-server-start.sh config/server.properties &
sleep 10

# ۲. بازگشت به ریپو و اجرای سرویس‌های پایتون
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS
python3 -m src.core_services.agent_registry_service.main &
python3 -m src.core_services.bl07_policy_plane_service_v1.main &
python3 -m src.core_services.bl08_permit_service_v1.main &
python3 -m src.core_services.audit_sink.main &
python3 -m src.governance_console.app.main &

# ۳. اجرای کامپایلر خودکار اسکیما
cd src/infrastructure/agent_schema_compiler && python3 compiler.py &

# ۴. اجرای UI (داشبورد)
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS/ui && python3 -m http.server 8089 &

echo "✅ همه سرویس‌ها بالا آمدند! به http://localhost:8089 بروید."
echo "برای مشاهده لاگ‌ها: tail -f logs.txt"
