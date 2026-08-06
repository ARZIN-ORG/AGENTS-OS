#!/bin/bash
set -e

echo "🚀 شروع استقرار کامل سیستم عامل ایجنت..."

# ۱. بالا آوردن کافکا و زیرساخت
echo "🔄 بالا آوردن کافکا و سرویس‌های هسته..."
cd deployment && docker-compose -f docker-compose.core.yml up -d

# ۲. صبر کردن برای بالا آمدن کافکا
echo "⏳ صبر برای کافکا..."
sleep 10

# ۳. اجرای کامپایلر برای ساخت توپیک‌ها و اسکیماها
echo "🔄 اجرای کامپایلر هوشمند..."
cd ../src/infrastructure/agent_schema_compiler && python compiler.py

# ۴. بالا آوردن سرویس UI
echo "🚀 بالا آوردن داشبورد UI..."
cd ../../ui && python3 -m http.server 8089 &

echo "✅ همه چیز آماده است!"
echo "💡 داشبورد UI: http://localhost:8089"
echo "💡 برای مشاهده لاگ‌ها: cd deployment && docker-compose logs -f"
