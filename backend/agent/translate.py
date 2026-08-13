"""NL -> structured plan. Deterministic templates (offline) only."""

import re
import sqlite3
from datetime import datetime, timedelta
from .. import config
from . import tools

def _parse_window(q: str) -> tuple[str | None, str | None]:
    now = datetime.fromisoformat(tools.REFERENCE_ISO)
    m = re.search(r"last\s+(\d+)\s+days?", q.lower())
    if m:
        days = int(m.group(1))
        since = (now - timedelta(days=days)).isoformat(timespec="seconds")
        return since, now.isoformat(timespec="seconds")
    return None, None

def template_translate(conn: sqlite3.Connection, question: str) -> dict:
    q = question.lower()
    steps = ["Step 1: Parsing question (template translator)"]
    
    fm = re.search(r"(?:flag|file)[-_\s]?(\d+)", q)
    if fm and ("similar" in q or "like" in q):
        rank = int(fm.group(1))
        row = conn.execute(
            "SELECT file_id FROM flags ORDER BY score DESC, id LIMIT 1 OFFSET ?", (max(0, rank - 1),)
        ).fetchone()
        if row is None:
            return {"intent": "case_summary", "params": {}, "steps": steps + ["Step 2: Flag not found"]}
        file_id = row["file_id"]
        steps.append(f"Step 2: Resolving flag #{rank} -> file {file_id}")
        steps.append("Step 3: Running perceptual-hash neighborhood search")
        return {"intent": "find_files_similar_to", "params": {"file_id": file_id}, "steps": steps}

    if "most active" in q or "active at night" in q:
        night = "night" in q
        since, until = _parse_window(q)
        if night:
            steps.append("Step 2: Filtering messages to night hours (00:00-04:00)")
        steps.append("Step 3: Grouping by sender and ranking by volume")
        return {
            "intent": "most_active_contact",
            "params": {"since": since, "until": until, "night_only": night},
            "steps": steps,
        }

    if "modified after" in q or "changed after" in q:
        ts = config.SEIZURE_ISO
        steps.append("Step 2: Using seizure timestamp as cutoff")
        steps.append("Step 3: Querying files by modification timestamp")
        return {"intent": "files_modified_after", "params": {"ts": ts}, "steps": steps}

    entities = tools.resolve_entity(conn, question)
    if entities and ("mention" in q or "about" in q or "conversation" in q or "talk" in q or "who" in q):
        entity = entities[0]
        since, until = _parse_window(q)
        steps.append(f"Step 2: Resolved entity: {entity['kind']} '{entity['name']}'")
        if since:
            steps.append(f"Step 3: Filtering window: {since[:10]} .. {until[:10]}")
        steps.append("Step 4: Graph query: messages mentioning entity")
        return {
            "intent": "find_messages_mentioning",
            "params": {"entity": entity["name"], "since": since, "until": until},
            "steps": steps,
        }

    steps.append("Step 2: No specific intent matched")
    return {"intent": "unsupported", "params": {}, "steps": steps}
