# Makefile برای مدیریت پروژه AgentOS
# استفاده: make [command]

.PHONY: up down build clean dev

# اجرای کامل پروژه با داکر
up:
	@echo "🚀 بالا آوردن سرویس‌های هسته (BL01-08)..."
	cd deployment && docker-compose -f docker-compose.core.yml up -d
	@echo "✅ سرویس‌های هسته فعال شدند."
	@echo "💡 برای مشاهده UI، به http://localhost:8089 مراجعه کنید."

# متوقف کردن سرویس‌ها
down:
	cd deployment && docker-compose -f docker-compose.core.yml down

# ساخت مجدد ایمیج‌های داکر
build:
	cd deployment && docker-compose -f docker-compose.core.yml build

# اجرای در حالت توسعه (بدون داکر، برای دیباگ سریع)
dev:
	@echo "🛠️ اجرای سرویس‌ها به‌صورت محلی (توسعه)..."
	@echo "۱. اجرای سرویس‌های پایتون:"
	cd src/core_services/agent_registry_service && python -m app.main &
	cd src/governance_console && python -m app.main &
	@echo "۲. اجرای سرور UI:"
	cd ui && python3 -m http.server 8089 &
	@echo "✅ محیط توسعه آماده است (پورت 8089)."

# پاک‌سازی فایل‌های موقت
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} \; 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "🧹 پاک‌سازی انجام شد."

# کامپایل خودکار اسکیماهای ایجنت
compile:
	@echo "🔄 اجرای کامپایلر زیرساختی..."
	cd src/infrastructure/agent_schema_compiler && python compiler.py

.PHONY: compile

# استقرار کامل: بالا آوردن سرویس‌های داکر + کامپایلر
deploy: compile up
	@echo "🚀 کل سیستم (کافکا + سرویس‌ها + کامپایلر) بالا آمد!"

# کامپایل خودکار و ساخت اسکیما
compile:
	@echo "🔄 اجرای کامپایلر زیرساختی..."
	cd src/infrastructure/agent_schema_compiler && python compiler.py

.PHONY: deploy compile
