"""Explanation layer — deterministic template only (minimal demo)."""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

@dataclass
class Explanation:
    text: str
    source: str

def build_evidence(conn: sqlite3.Connection, flag_id: int) -> dict:
    flag = conn.execute("SELECT * FROM flags WHERE id=?", (flag_id,)).fetchone()
    if flag is None:
        return {}
    file_row = conn.execute("SELECT * FROM files WHERE id=?", (flag["file_id"],)).fetchone()
    rules = conn.execute(
        "SELECT rule, points, detail, plain_label FROM rules_fired WHERE flag_id=? ORDER BY points DESC",
        (flag_id,),
    ).fetchall()
    return {
        "file": {"name": file_row["name"]},
        "score": flag["score"],
        "severity": flag["severity"],
        "rules_fired": [dict(r) for r in rules],
    }

class ExplanationProvider:
    def __init__(self, llm=None):
        pass

    def explain(self, evidence: dict) -> Explanation:
        f = evidence.get("file", {})
        name = f.get("name", "file")
        sev = evidence.get("severity", "low")
        score = evidence.get("score", 0)
        rules = evidence.get("rules_fired", [])
        
        if not rules:
            labels = "None"
        else:
            labels = " • ".join(r.get("plain_label", r.get("rule")) for r in rules)
        
        text = f"Flagged {name} — {sev} risk ({score}/100). Triggered {len(rules)} rule(s): • {labels}. Review the evidence and decide."
        
        return Explanation(text=text, source="template")
