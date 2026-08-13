"""SQLite layer — schema, connection, helpers."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS scan_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    files_total INTEGER DEFAULT 0,
    files_processed INTEGER DEFAULT 0,
    seizure_ts TEXT,
    reference_ts TEXT
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    ext TEXT,
    size_bytes INTEGER,
    created_ts TEXT,
    modified_ts TEXT,
    sha256 TEXT,
    phash TEXT,
    is_image INTEGER DEFAULT 0,
    is_chat INTEGER DEFAULT 0,
    is_hidden INTEGER DEFAULT 0,
    magic TEXT,
    scan_run_id INTEGER
);

CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    channel TEXT,
    contact TEXT,
    chat_file_id INTEGER,
    participants TEXT,
    msg_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conv_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    ts TEXT NOT NULL,
    text TEXT NOT NULL,
    mentions_location INTEGER DEFAULT 0,
    coded_marker INTEGER DEFAULT 0,
    night_hour INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS hash_matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    hash_type TEXT NOT NULL,          -- 'sha256' | 'phash'
    known_id TEXT NOT NULL,           -- MOCK-xxxx
    confidence REAL NOT NULL,
    distance INTEGER
);

CREATE TABLE IF NOT EXISTS flags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    severity TEXT NOT NULL,
    score INTEGER NOT NULL,
    rule_names_json TEXT NOT NULL,
    explanation TEXT,
    explain_source TEXT DEFAULT 'template',   -- 'llm' | 'template'
    decision TEXT,                            -- NULL | 'reviewed' | 'dismissed' | 'escalated'
    decision_ts TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rules_fired (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flag_id INTEGER NOT NULL,
    rule TEXT NOT NULL,
    points INTEGER NOT NULL,
    detail TEXT,
    plain_label TEXT
);

CREATE TABLE IF NOT EXISTS timeline_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    kind TEXT NOT NULL,               -- scan_started | ingest_done | flag_found | query | decision | scan_done ...
    title TEXT NOT NULL,
    detail TEXT
);

CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    db_path = db_path or config.DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]


def reset_db() -> None:
    """Wipe all case data (keeps schema). Used by tests and 'new case'."""
    conn = connect()
    try:
        conn.executescript(
            """
            DELETE FROM rules_fired; DELETE FROM flags; DELETE FROM hash_matches;
            DELETE FROM chat_messages; DELETE FROM conversations; DELETE FROM files;
            DELETE FROM scan_runs; DELETE FROM timeline_events; DELETE FROM meta;
            """
        )
        conn.commit()
    finally:
        conn.close()


def json_dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def json_loads(s: str | None):
    if not s:
        return None
    return json.loads(s)
