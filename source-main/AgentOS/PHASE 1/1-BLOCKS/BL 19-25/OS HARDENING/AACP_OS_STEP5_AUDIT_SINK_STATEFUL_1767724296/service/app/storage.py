from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, List, Tuple
import os
import sqlite3
import threading

from .config import Settings
from .util import now_ms, new_id

_SCHEMA_SQL = '''
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS audit_records (
  id TEXT PRIMARY KEY,
  seq INTEGER NOT NULL UNIQUE,
  ts_ms INTEGER NOT NULL,
  trace_id TEXT NOT NULL,
  event_id TEXT NOT NULL,
  channel_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  producer_id TEXT NOT NULL,
  consumer_id TEXT NOT NULL,
  policy_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  permit_id TEXT NOT NULL,
  intent_id TEXT NOT NULL,
  payload_digest TEXT,
  prev_chain_hash TEXT,
  chain_hash TEXT NOT NULL,
  envelope_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_records(ts_ms);
CREATE INDEX IF NOT EXISTS idx_audit_trace ON audit_records(trace_id);
CREATE INDEX IF NOT EXISTS idx_audit_topic ON audit_records(topic);
'''

@dataclass
class SQLiteStore:
    settings: Settings
    _conn: sqlite3.Connection
    _lock: threading.Lock

    @staticmethod
    def open(settings: Settings) -> "SQLiteStore":
        os.makedirs(os.path.dirname(settings.sqlite_path), exist_ok=True)
        conn = sqlite3.connect(settings.sqlite_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
        return SQLiteStore(settings=settings, _conn=conn, _lock=threading.Lock())

    def _next_seq(self) -> int:
        cur = self._conn.execute("SELECT COALESCE(MAX(seq),0) AS m FROM audit_records")
        row = cur.fetchone()
        return int(row["m"]) + 1

    def append(self, envelope: Dict[str, Any], payload_digest: Optional[str], prev_chain_hash: Optional[str], chain_hash: str) -> Tuple[str,int,int]:
        with self._lock:
            seq = self._next_seq()
            ts_ms = now_ms()
            rid = new_id("aud")
            # Required fields: fail-fast if missing
            trace_id = str(envelope.get("trace_id",""))
            event_id = str(envelope.get("event_id",""))
            channel_id = str(envelope.get("channel_id",""))
            topic = str(envelope.get("topic",""))
            producer_id = str(envelope.get("producer_id",""))
            consumer_id = str(envelope.get("consumer_id",""))
            policy_id = str(envelope.get("policy_id",""))
            policy_version = str(envelope.get("policy_version",""))
            permit_id = str(envelope.get("permit_id",""))
            intent_id = str(envelope.get("intent_id",""))
            if not all([trace_id,event_id,channel_id,topic,producer_id,consumer_id,policy_id,policy_version,permit_id,intent_id]):
                raise ValueError("Missing required envelope fields for audit storage")

            import json
            env_json = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            self._conn.execute(
                """INSERT INTO audit_records
                (id, seq, ts_ms, trace_id, event_id, channel_id, topic, producer_id, consumer_id,
                 policy_id, policy_version, permit_id, intent_id, payload_digest, prev_chain_hash, chain_hash, envelope_json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rid, seq, ts_ms, trace_id, event_id, channel_id, topic, producer_id, consumer_id,
                 policy_id, policy_version, permit_id, intent_id, payload_digest, prev_chain_hash, chain_hash, env_json)
            )
            self._conn.commit()
            return rid, seq, ts_ms

    def get_by_id(self, rid: str) -> Optional[Dict[str, Any]]:
        cur = self._conn.execute("SELECT * FROM audit_records WHERE id=?", (rid,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        cur = self._conn.execute("SELECT * FROM audit_records ORDER BY seq DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    def last_chain_hash(self) -> Optional[str]:
        cur = self._conn.execute("SELECT chain_hash FROM audit_records ORDER BY seq DESC LIMIT 1")
        row = cur.fetchone()
        return str(row["chain_hash"]) if row else None

    def retention_cleanup(self, retention_days: int) -> int:
        cutoff_ms = now_ms() - int(retention_days) * 24 * 60 * 60 * 1000
        cur = self._conn.execute("DELETE FROM audit_records WHERE ts_ms < ?", (cutoff_ms,))
        self._conn.commit()
        return int(cur.rowcount)
