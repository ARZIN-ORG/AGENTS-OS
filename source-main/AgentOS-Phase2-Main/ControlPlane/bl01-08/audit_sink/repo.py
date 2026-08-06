from __future__ import annotations

from datetime import datetime
import json
from sqlalchemy.orm import Session

from .models import AuditRecord

def insert_record(db: Session, payload: dict) -> AuditRecord:
    now = datetime.utcnow()
    raw = payload.get("raw")
    rec = AuditRecord(
        trace_id=payload["trace_id"],
        message_id=payload.get("message_id"),
        channel_id=payload["channel_id"],
        topic=payload["topic"],
        agent_id=payload["agent_id"],
        agent_class=payload["agent_class"],
        decision=payload["decision"],
        reason_code=payload["reason_code"],
        policy_id=payload.get("policy_id"),
        policy_version=payload.get("policy_version"),
        signature_valid=bool(payload.get("signature_valid", False)),
        envelope_hash=payload.get("envelope_hash"),
        chain_hash=payload.get("chain_hash"),
        event_time=payload.get("event_time") or now,
        received_time=now,
        raw=json.dumps(raw, ensure_ascii=False) if isinstance(raw, (dict, list)) else None,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
