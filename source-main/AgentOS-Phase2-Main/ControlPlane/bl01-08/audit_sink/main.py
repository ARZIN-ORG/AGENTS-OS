from __future__ import annotations

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import SessionLocal, ENGINE
from .models import Base, AuditRecord
from .schemas import AacpAuditRecordIn, AacpAuditRecordOut
from .repo import insert_record

app = FastAPI(title="ARZIN AACP Audit Sink", version="2.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=ENGINE)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/v1/audit/records", response_model=AacpAuditRecordOut)
def create_record(payload: AacpAuditRecordIn, db: Session = Depends(get_db)):
    try:
        rec = insert_record(db, payload.model_dump())
        return AacpAuditRecordOut(
            id=rec.id,
            trace_id=rec.trace_id,
            message_id=rec.message_id,
            channel_id=rec.channel_id,
            topic=rec.topic,
            agent_id=rec.agent_id,
            agent_class=rec.agent_class,
            decision=rec.decision,
            reason_code=rec.reason_code,
            policy_id=rec.policy_id,
            policy_version=rec.policy_version,
            signature_valid=rec.signature_valid,
            envelope_hash=rec.envelope_hash,
            chain_hash=rec.chain_hash,
            event_time=rec.event_time,
            received_time=rec.received_time,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="audit_persist_failed")

@app.get("/v1/audit/records/by-trace/{trace_id}")
def by_trace(trace_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(AuditRecord)
        .where(AuditRecord.trace_id == trace_id)
        .order_by(AuditRecord.id.desc())
        .limit(200)
    ).scalars().all()
    return [
        {
            "id": r.id,
            "trace_id": r.trace_id,
            "message_id": r.message_id,
            "decision": r.decision,
            "reason_code": r.reason_code,
            "topic": r.topic,
            "received_time": r.received_time.isoformat(),
        }
        for r in rows
    ]

@app.get("/v1/audit/records/by-message/{message_id}")
def by_message(message_id: str, db: Session = Depends(get_db)):
    rows = db.execute(
        select(AuditRecord)
        .where(AuditRecord.message_id == message_id)
        .order_by(AuditRecord.id.desc())
        .limit(50)
    ).scalars().all()
    return [
        {
            "id": r.id,
            "trace_id": r.trace_id,
            "message_id": r.message_id,
            "decision": r.decision,
            "reason_code": r.reason_code,
            "topic": r.topic,
            "received_time": r.received_time.isoformat(),
        }
        for r in rows
    ]
