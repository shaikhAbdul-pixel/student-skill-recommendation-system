"""Opt-in local SQLite storage, isolated by an ephemeral Streamlit session token."""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from src.catalog import ROOT


@contextmanager
def connect(db_path=None):
    path = db_path or ROOT / "local_data" / "plans.sqlite3"
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        with connection:
            connection.execute("CREATE TABLE IF NOT EXISTS plans (id TEXT PRIMARY KEY, session_id TEXT NOT NULL, created_at TEXT NOT NULL, payload TEXT NOT NULL)")
            yield connection
    finally:
        connection.close()


def save_plan(session_id, payload, db_path=None):
    plan_id = str(uuid.uuid4())
    with connect(db_path) as db:
        db.execute("INSERT INTO plans VALUES (?, ?, ?, ?)",
                   (plan_id, session_id, datetime.now(timezone.utc).isoformat(), json.dumps(payload)))
    return plan_id


def list_plans(session_id, db_path=None):
    with connect(db_path) as db:
        rows = db.execute("SELECT id, created_at, payload FROM plans WHERE session_id=? ORDER BY created_at DESC", (session_id,)).fetchall()
    return [{"id": r[0], "created_at": r[1], "payload": json.loads(r[2])} for r in rows]


def delete_plans(session_id, db_path=None):
    with connect(db_path) as db:
        db.execute("DELETE FROM plans WHERE session_id=?", (session_id,))
