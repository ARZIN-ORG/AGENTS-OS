from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, Text, Index
from datetime import datetime

class Base(DeclarativeBase):
    pass

class AuditRecord(Base):
    __tablename__ = "aacp_audit_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    trace_id: Mapped[str] = mapped_column(String(128), index=True)
    message_id: Mapped[str | None] = mapped_column(String(128), index=True, nullable=True)

    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    topic: Mapped[str] = mapped_column(String(256), index=True)

    agent_id: Mapped[str] = mapped_column(String(128), index=True)
    agent_class: Mapped[str] = mapped_column(String(128), index=True)

    decision: Mapped[str] = mapped_column(String(16), index=True)  # ALLOW/DENY
    reason_code: Mapped[str] = mapped_column(String(128), index=True)

    policy_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    policy_version: Mapped[int | None] = mapped_column(Integer, nullable=True)

    signature_valid: Mapped[bool] = mapped_column(Boolean, default=False)

    envelope_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    chain_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    received_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    raw: Mapped[str | None] = mapped_column(Text, nullable=True)

Index("ix_aacp_audit_trace_msg", AuditRecord.trace_id, AuditRecord.message_id)
