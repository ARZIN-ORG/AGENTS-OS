# -*- coding: utf-8 -*-
from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    service_name: str = os.getenv("ARZIN_SERVICE_NAME", "policy-plane-service")
    bind_host: str = os.getenv("ARZIN_BIND_HOST", "0.0.0.0")
    bind_port: int = int(os.getenv("ARZIN_BIND_PORT", "8081"))
    database_url: str = os.getenv("ARZIN_DATABASE_URL", "sqlite:///./policy_plane.db")
    log_enabled: bool = os.getenv("ARZIN_LOG_ENABLED", "true").lower() == "true"
    phase: str = os.getenv("ARZIN_PHASE", "phase1")
