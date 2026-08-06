# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text

class Base(DeclarativeBase):
    pass

class IntentRow(Base):
    __tablename__ = "intents"

    intent_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    created_at_utc: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    original_input: Mapped[str] = mapped_column(Text, nullable=False)

    action_type: Mapped[str] = mapped_column(String(128), nullable=False)
    target_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    parameters_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    rationale: Mapped[str] = mapped_column(String(1000), nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="DRAFT")
    reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    reviewed_at_utc: Mapped[str] = mapped_column(String(64), nullable=True)
    finalized_by: Mapped[str] = mapped_column(String(128), nullable=True)
    finalized_at_utc: Mapped[str] = mapped_column(String(64), nullable=True)
    final_approval_id: Mapped[str] = mapped_column(String(128), nullable=True)
    trace_id: Mapped[str] = mapped_column(String(128), nullable=True)
