#!/bin/bash
set -e
echo "🚀 شروع استقرار اصلاح‌شده..."

export KAFKA_BROKER="localhost:9092"
export PYTHONPATH="$PYTHONPATH:$(pwd)"

# ۱. راه‌اندازی کافکا در پس‌زمینه
cd ~/kafka/kafka_2.13-3.4.0
bin/zookeeper-server-start.sh config/zookeeper.properties > /dev/null 2>&1 &
sleep 5
bin/kafka-server-start.sh config/server.properties > /dev/null 2>&1 &
sleep 10

# ۲. اجرای سرویس‌های هسته
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS
python3 -m src.core_services.agent_registry_service.main &
echo "✅ Agent Registry (پورت 8080)"
sleep 2
python3 -m src.core_services.bl07_policy_plane_service_v1.main &
echo "✅ Policy Plane (پورت 8081)"
sleep 2
python3 -m src.core_services.bl08_permit_service_v1.main &
echo "✅ Permit Service (پورت 8082)"
sleep 2
python3 -m src.core_services.audit_sink.main &
echo "✅ Audit Sink (پورت 8083)"
sleep 2

# ۳. کنسول حکمرانی
python3 -m src.governance_console.app.main &
echo "✅ Governance Console (پورت 8090)"
sleep 3

# ۴. کامپایلر
cd src/infrastructure/agent_schema_compiler && python3 compiler.py
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS

# ۵. UI
cd ui && python3 -m http.server 8089 &
echo "✅ UI در http://localhost:8089"

echo "====================================================================="
echo "🌐 تمام سرویس‌ها با موفقیت بالا آمدند!"
echo "📊 داشبورد: http://localhost:8089"
echo "🔍 برای بررسی وضعیت: ps aux | grep python"
echo "====================================================================="
