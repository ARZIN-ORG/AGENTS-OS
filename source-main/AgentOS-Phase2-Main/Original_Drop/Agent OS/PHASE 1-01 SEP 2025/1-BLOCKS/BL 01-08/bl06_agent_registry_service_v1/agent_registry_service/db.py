# -*- coding: utf-8 -*-
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import Settings
from .models import Base


def make_engine(settings: Settings):
    # pool_pre_ping helps in private-cloud deployments where connections may drop.
    return create_engine(settings.database_url, pool_pre_ping=True, future=True)


def init_db(engine) -> None:
    Base.metadata.create_all(bind=engine)


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session, future=True)


@contextmanager
def session_scope(SessionLocal) -> Iterator[Session]:
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
