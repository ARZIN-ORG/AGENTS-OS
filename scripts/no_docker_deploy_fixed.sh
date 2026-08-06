#!/bin/bash
set -e
echo "🚀 شروع استقرار کامل سیستم بدون کانتینر..."

# تنظیم آدرس کافکا
export KAFKA_BROKER="localhost:9092"

# ۱. راه‌اندازی کافکا (اگر قبلاً روشن نیست)
echo "🔄 بررسی و راه‌اندازی کافکا و زوکیپر..."
cd ~/kafka/kafka_2.13-3.4.0

# اگر زوکیپر در حال اجراست، آن را نکشیم
if ! pgrep -f "zookeeper-server-start"; then
    bin/zookeeper-server-start.sh config/zookeeper.properties &
    echo "⏳ منتظر بالا آمدن زوکیپر (۵ ثانیه)..."
    sleep 5
else
    echo "ℹ️ زوکیپر از قبل در حال اجراست."
fi

if ! pgrep -f "kafka-server-start"; then
    bin/kafka-server-start.sh config/server.properties &
    echo "⏳ منتظر بالا آمدن کافکا (۱۰ ثانیه)..."
    sleep 10
else
    echo "ℹ️ کافکا از قبل در حال اجراست."
fi

# ۲. بازگشت به ریپو و راه‌اندازی سرویس‌های پایتون
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS

echo "🔄 راه‌اندازی سرویس‌های هسته (BL01-BL08)..."
python3 -m src.core_services.agent_registry_service.main &
echo "✅ Agent Registry شروع شد (پورت 8080)"
sleep 2

python3 -m src.core_services.bl07_policy_plane_service_v1.main &
echo "✅ Policy Plane شروع شد (پورت 8081)"
sleep 2

python3 -m src.core_services.bl08_permit_service_v1.main &
echo "✅ Permit Service شروع شد (پورت 8082)"
sleep 2

python3 -m src.core_services.audit_sink.main &
echo "✅ Audit Sink شروع شد (پورت 8083)"
sleep 2

echo "🔄 راه‌اندازی سرویس کنسول حکمرانی (BL19)..."
python3 -m src.governance_console.app.main &
echo "✅ Governance Console شروع شد (پورت 8090)"
sleep 3

echo "🔄 اجرای کامپایلر و ایجاد توپیک‌های کافکا..."
cd src/infrastructure/agent_schema_compiler && python3 compiler.py
cd /home/zi/WORKSPACES/SHARED/AGENTS-OS

echo "🔄 راه‌اندازی رابط کاربری (UI)..."
cd ui && python3 -m http.server 8089 &
echo "✅ UI در پورت 8089 در دسترس است."

echo ""
echo "====================================================================="
echo "🌐 تمام سرویس‌ها با موفقیت بالا آمدند!"
echo "📊 داشبورد: http://localhost:8089"
echo "🔍 برای بررسی وضعیت سرویس‌ها: ps aux | grep python"
echo "====================================================================="
