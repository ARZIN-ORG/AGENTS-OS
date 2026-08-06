# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import FastAPI

from .settings import Settings
from .logging import Logger
from .db import make_engine, init_db, make_session_factory, session_scope
from .api import router


_settings = Settings()
_logger = Logger("agent-registry", enabled=_settings.log_enabled)

_engine = make_engine(_settings)
init_db(_engine)
_SessionLocal = make_session_factory(_engine)


def get_session():
    return session_scope(_SessionLocal)


def create_app() -> FastAPI:
    app = FastAPI(title="ARZIN Agent Registry Service", version="1.0")
    app.include_router(router)

    @app.on_event("startup")
    def _startup() -> None:
        _logger.info("startup", service=_settings.service_name, db=_settings.database_url)

    return app


app = create_app()
