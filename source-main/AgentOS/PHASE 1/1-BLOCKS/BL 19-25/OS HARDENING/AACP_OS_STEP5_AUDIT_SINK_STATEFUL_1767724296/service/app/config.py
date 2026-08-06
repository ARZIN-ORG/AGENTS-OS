from __future__ import annotations
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    db_url: str
    sqlite_path: str
    enforce_chain: bool
    retention_days: int
    enable_retention: bool
    service_name: str

def load_settings() -> Settings:
    db_url = os.getenv("AACP_AUDIT_DB_URL", "").strip()
    sqlite_path = os.getenv("AACP_AUDIT_SQLITE_PATH", "/var/lib/aacp/audit.db")
    enforce_chain = os.getenv("AACP_AUDIT_ENFORCE_CHAIN", "false").lower() in ("1","true","yes")
    retention_days = int(os.getenv("AACP_AUDIT_RETENTION_DAYS", "365"))
    enable_retention = os.getenv("AACP_AUDIT_ENABLE_RETENTION", "true").lower() in ("1","true","yes")
    service_name = os.getenv("AACP_SERVICE_NAME", "audit_sink_service")
    return Settings(
        db_url=db_url,
        sqlite_path=sqlite_path,
        enforce_chain=enforce_chain,
        retention_days=retention_days,
        enable_retention=enable_retention,
        service_name=service_name,
    )
