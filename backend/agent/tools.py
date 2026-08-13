"""Agent tools — each returns (result, step_description) so the reasoning log is human-readable."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

from .. import config
from ..graph.kg import build_graph, graph_json

REFERENCE_ISO = config.CASE_REFERENCE_ISO


def _now() -> datetime:
    return datetime.fromisoformat(REFERENCE_ISO)


def resolve_entity(conn: sqlite3.Connection, name: str) -> list[dict]:
    """Resolve a plain-English entity mention to known entities."""
    name = name.strip().lower()
    hits = []
    for loc in config.LOCATIONS:
        if loc.lower() in name:
            hits.append({"kind": "location", "name": loc})
    for p in config.PERSONS:
        if p.lower() in name:
            hits.append({"kind": "person", "name": p})
    # conversation/file name match
    for c in conn.execute("SELECT id, title FROM conversations"):
        if c["title"].lower() in name:
            hits.append({"kind": "conversation", "name": c["title"], "id": c["id"]})
    return hits


def find_messages_mentioning(
    conn: sqlite3.Connection, entity: str, since: str | None = None, until: str | None = None
) -> tuple[list[dict], str]:
    """Messages whose text mentions `entity` (a location or person name)."""
    rows = conn.execute(
        """
        SELECT m.*, c.title AS conv_title
        FROM chat_messages m JOIN conversations c ON c.id = m.conv_id
        WHERE lower(m.text) LIKE ?
        ORDER BY m.ts
        """,
        (f"%{entity.lower()}%",),
    ).fetchall()
    out = []
    for r in rows:
        ts = datetime.fromisoformat(r["ts"])
        if since and ts < datetime.fromisoformat(since):
            continue
        if until and ts > datetime.fromisoformat(until):
            continue
        out.append(
            {
                "message_id": r["id"],
                "conversation": r["conv_title"],
                "sender": r["sender"],
                "ts": r["ts"],
                "text": r["text"],
                "night": bool(r["night_hour"]),
            }
        )
    step = f"Graph query: messages mentioning '{entity}'" + (
        f" between {since} and {until}" if since or until else ""
    )
    return out, step


def most_active_contact(
    conn: sqlite3.Connection, since: str | None = None, until: str | None = None, night_only: bool = False
) -> tuple[list[dict], str]:
    """Rank contacts by message count in a window, optionally night-only."""
    q = """
        SELECT sender, COUNT(*) AS n
        FROM chat_messages
        WHERE 1=1
    """
    params: list = []
    if night_only:
        q += " AND night_hour=1"
    if since:
        q += " AND ts >= ?"
        params.append(since)
    if until:
        q += " AND ts <= ?"
        params.append(until)
    q += " GROUP BY sender ORDER BY n DESC"
    rows = conn.execute(q, params).fetchall()
    out = [{"contact": r["sender"], "count": r["n"]} for r in rows]
    step = "Graph query: group messages by sender" + (" (night hours only)" if night_only else "")
    return out, step


def find_files_similar_to(conn: sqlite3.Connection, file_id: int) -> tuple[list[dict], str]:
    """Perceptually similar images (phash distance <= threshold)."""
    row = conn.execute("SELECT phash FROM files WHERE id=?", (file_id,)).fetchone()
    if not row or not row["phash"]:
        return [], f"File {file_id}: no image hash available"
    from ..scan.hashing import phash_bits

    target = phash_bits(row["phash"])
    out = []
    for r in conn.execute("SELECT id, name, phash FROM files WHERE is_image=1 AND id<>?", (file_id,)):
        if not r["phash"]:
            continue
        dist = int((target ^ phash_bits(r["phash"])).sum())
        if dist <= config.PHASH_THRESHOLD:
            out.append(
                {"file_id": r["id"], "name": r["name"], "distance": dist,
                 "similarity": round(1 - dist / 64, 3)}
            )
    out.sort(key=lambda x: x["distance"])
    step = f"Graph query: perceptual-hash neighbors of file {file_id}"
    return out, step


def files_modified_after(conn: sqlite3.Connection, ts: str) -> tuple[list[dict], str]:
    rows = conn.execute(
        "SELECT id, name, path, modified_ts FROM files WHERE modified_ts > ? ORDER BY modified_ts",
        (ts,),
    ).fetchall()
    out = [dict(r) for r in rows]
    step = f"Query: files modified after {ts}"
    return out, step


def get_graph(conn: sqlite3.Connection, focus: str | None = None, depth: int = 2,
              pos: dict | None = None) -> dict:
    G = build_graph(conn)
    return graph_json(G, focus=focus, depth=depth, pos=pos)
