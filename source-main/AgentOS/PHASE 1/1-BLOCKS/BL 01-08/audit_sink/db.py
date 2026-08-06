from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_url() -> str:
    return os.getenv("AUDIT_DB_URL", "sqlite:////app/audit.db")

ENGINE = create_engine(get_db_url(), future=True)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, future=True)
