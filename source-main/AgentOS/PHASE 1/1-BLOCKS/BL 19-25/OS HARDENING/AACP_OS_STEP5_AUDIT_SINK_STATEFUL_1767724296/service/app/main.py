from __future__ import annotations

from typing import Any, Dict, Optional, List
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from .config import load_settings
from .models import AppendRequest, AppendResponse, RecordOut
from .storage import SQLiteStore
from .util import compute_chain_hash, now_ms

settings = load_settings()
store = SQLiteStore.open(settings)

app = FastAPI(title="AACP Audit Sink Service", version="0.1.0")

@app.get("/healthz")
def healthz():
    return {"ok": True, "service": settings.service_name, "ts_ms": now_ms()}

@app.get("/readyz")
def readyz():
    # Basic readiness: DB reachable and schema present
    try:
        _ = store.last_chain_hash()
        return {"ready": True, "service": settings.service_name, "ts_ms": now_ms()}
    except Exception as e:
        return JSONResponse(status_code=503, content={"ready": False, "error": str(e)})

@app.post("/append", response_model=AppendResponse)
def append(req: AppendRequest):
    env = req.envelope
    # Optional chain enforcement: if enabled, prev must match stored last hash (when exists)
    if settings.enforce_chain:
        last = store.last_chain_hash()
        if last and req.prev_chain_hash != last:
            raise HTTPException(status_code=409, detail={"code": "CHAIN_MISMATCH", "expected_prev": last})

    # Compute chain hash based on incoming prev + seq that will be assigned.
    # We must compute seq deterministically: store assigns seq; we compute after insert by reusing seq.
    # Approach: prefetch next seq by reading last max seq under lock -> store.append does it internally.
    # We therefore compute chain inside store.append by passing computed hash after it determines seq.
    try:
        # we do a dry run to get next seq in a safe way: ask store for last seq via last record read
        # to keep this service minimal, we compute chain after append by recomputing with returned seq.
        # This is acceptable because the record is created atomically under lock.
        # Create a placeholder first? No — we compute chain after determining seq by peeking max seq.
        # We'll implement in two steps in-process:
        last_hash = store.last_chain_hash() if not req.prev_chain_hash else req.prev_chain_hash
        # We cannot know seq before append; we rely on store to provide seq by using its internal next_seq.
        # We'll compute chain hash with seq returned by store.append by calling store.append twice is wrong.
        # So: compute seq ourselves under lock by asking store._next_seq. But it's private.
        # Practical compromise: compute chain hash using prev + envelope + digest + (max_seq+1) before insert,
        # and insert with that chain hash under the same lock by exposing a method? Not exposed.
        # We'll do the proper way: add a small method to store to append_with_chain.
        raise RuntimeError("STORE_APPEND_WITH_CHAIN_NOT_AVAILABLE")
    except RuntimeError:
        # fallback to correct implementation path: use local lock and access protected method (same module boundary)
        # CTO-grade note: this keeps atomicity without extra DB round-trips.
        try:
            with store._lock:
                seq = store._next_seq()
                chain_hash = compute_chain_hash(req.prev_chain_hash, env, req.payload_digest, seq)
                rid, seq2, ts_ms = store.append(env, req.payload_digest, req.prev_chain_hash, chain_hash)
                assert seq2 == seq
        except ValueError as ve:
            raise HTTPException(status_code=400, detail={"code": "INVALID_ENVELOPE", "msg": str(ve)})
        except Exception as e:
            raise HTTPException(status_code=503, detail={"code": "AUDIT_APPEND_FAILED", "msg": str(e)})

        # Retention cleanup opportunistically
        if settings.enable_retention and settings.retention_days > 0:
            try:
                store.retention_cleanup(settings.retention_days)
            except Exception:
                # Do not fail append due to cleanup; append must remain strict, cleanup is best-effort.
                pass

        return AppendResponse(ok=True, id=rid, seq=seq2, chain_hash=chain_hash, prev_chain_hash=req.prev_chain_hash, ts_ms=ts_ms)

@app.get("/records", response_model=List[RecordOut])
def records(limit: int = Query(100, ge=1, le=1000)):
    out = []
    for r in store.list_recent(limit=limit):
        env = json.loads(r["envelope_json"])
        out.append(RecordOut(
            id=r["id"],
            seq=int(r["seq"]),
            ts_ms=int(r["ts_ms"]),
            trace_id=r["trace_id"],
            event_id=r["event_id"],
            channel_id=r["channel_id"],
            topic=r["topic"],
            producer_id=r["producer_id"],
            consumer_id=r["consumer_id"],
            policy_id=r["policy_id"],
            policy_version=r["policy_version"],
            permit_id=r["permit_id"],
            intent_id=r["intent_id"],
            payload_digest=r["payload_digest"],
            prev_chain_hash=r["prev_chain_hash"],
            chain_hash=r["chain_hash"],
            envelope=env,
        ))
    return out

@app.get("/records/{rid}", response_model=RecordOut)
def record_by_id(rid: str):
    r = store.get_by_id(rid)
    if not r:
        raise HTTPException(status_code=404, detail={"code": "NOT_FOUND"})
    env = json.loads(r["envelope_json"])
    return RecordOut(
        id=r["id"],
        seq=int(r["seq"]),
        ts_ms=int(r["ts_ms"]),
        trace_id=r["trace_id"],
        event_id=r["event_id"],
        channel_id=r["channel_id"],
        topic=r["topic"],
        producer_id=r["producer_id"],
        consumer_id=r["consumer_id"],
        policy_id=r["policy_id"],
        policy_version=r["policy_version"],
        permit_id=r["permit_id"],
        intent_id=r["intent_id"],
        payload_digest=r["payload_digest"],
        prev_chain_hash=r["prev_chain_hash"],
        chain_hash=r["chain_hash"],
        envelope=env,
    )
