اجرای محلی (Development)

۱) نصب وابستگی‌ها
pip install -r requirements.txt

۲) اجرا
export ARZIN_DATABASE_URL="sqlite:///./agent_registry.db"
python -m agent_registry_service.main

۳) تست سریع
curl -s http://localhost:8080/health

نکته:
در محیط Private Cloud، ARZIN_DATABASE_URL باید به Postgres اشاره کند.
