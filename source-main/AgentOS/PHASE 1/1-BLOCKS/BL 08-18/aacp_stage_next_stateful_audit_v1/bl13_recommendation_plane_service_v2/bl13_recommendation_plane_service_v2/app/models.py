# -*- coding: utf-8 -*-
from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Text

class Base(DeclarativeBase):
    pass

class SuggestionRow(Base):
    __tablename__ = "suggestions"

    suggestion_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    created_at_utc: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by_agent: Mapped[str] = mapped_column(String(128), nullable=False)
    audience: Mapped[str] = mapped_column(String(16), nullable=False)

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)

    domain: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    expected_impact_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    risk_notes_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    proposed_action_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="PROPOSED")
    status_reason: Mapped[str] = mapped_column(String(500), nullable=True)

    last_reviewed_by: Mapped[str] = mapped_column(String(128), nullable=True)
    last_reviewed_at_utc: Mapped[str] = mapped_column(String(64), nullable=True)
    human_final_approval_id: Mapped[str] = mapped_column(String(128), nullable=True)
