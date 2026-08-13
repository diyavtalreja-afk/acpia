from __future__ import annotations
import sqlite3
from datetime import datetime
from .. import artifact_spec, config, db as dbm
from .synthetic_check import score_image

SEV_LOW, SEV_MED, SEV_HIGH = "low", "medium", "high"

def severity_for(score: int) -> str:
    if score >= 70:
        return SEV_HIGH
    if score >= 40:
        return SEV_MED
    return SEV_LOW

def _seizure_ts() -> datetime:
    return datetime.fromisoformat(config.SEIZURE_ISO)

def assess_file(conn: sqlite3.Connection, file_id: int, target_path: Path) -> list[dict]:
    row = conn.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
    if row is None:
        return []
    fired: list[dict] = []
    
    # Exact points mapping from minimal spec
    POINTS = {
        "hash_match_exact": 50,
        "hash_match_phash": 35,
        "synthetic_media": 25,
        "renamed_extension": 20,
        "modified_after_seizure": 20,
        "location_night_activity": 15,
        "coded_language": 10,
        "hidden_file": 10,
        "bulk_duplication": 10,
    }

    def add(rule: str, detail: str):
        fired.append({"rule": rule, "points": POINTS[rule], "detail": detail})

    # --- Hash match ---
    exact_ids = {m["known_id"] for m in conn.execute(
        "SELECT * FROM hash_matches WHERE file_id=? AND hash_type='sha256'", (file_id,))}
    for m in conn.execute(
        "SELECT * FROM hash_matches WHERE file_id=? AND hash_type IN ('sha256','phash')", (file_id,)):
        if m["hash_type"] == "sha256":
            add("hash_match_exact", f"Known entry {m['known_id']} (byte-identical sha256:{row['sha256'][:12]}...)")
        elif m["known_id"] not in exact_ids:
            add("hash_match_phash", f"Known entry {m['known_id']} (visual distance {m['distance']}/64, confidence {m['confidence']})")

    # --- Synthetic media ---
    if row["is_image"]:
        path = target_path / row["path"]
        score = score_image(str(path))
        if score >= 0.8:
            add("synthetic_media", f"Synthetic correlation: {score:.3f}")

    # --- Renamed extension ---
    if row["magic"] and row["ext"]:
        magic_for_ext = {
            ".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".gif": "gif",
            ".pdf": "pdf", ".zip": "zip", ".json": "json", ".wav": "riff",
            ".txt": "text", ".md": "text", ".csv": "text", ".log": "text",
        }
        text_exts = {".txt", ".md", ".csv", ".log"}
        expected = magic_for_ext.get(row["ext"].lower())
        if expected and row["magic"] != expected:
            if not (row["magic"] == "text" and row["ext"] in text_exts):
                add("renamed_extension", f"Declared {row['ext']} but content is {row['magic'].upper()}")

    # --- Hidden file ---
    if row["is_hidden"]:
        add("hidden_file", f"Hidden marker in filename")

    # --- Modified after seizure ---
    try:
        mtime = datetime.fromisoformat(row["modified_ts"])
        if mtime.tzinfo is not None:
            after = mtime > _seizure_ts()
        else:
            after = mtime > _seizure_ts().replace(tzinfo=None)
        if after:
            add("modified_after_seizure", f"Modified after seizure")
    except (TypeError, ValueError):
        pass

    # --- Chat-derived rules ---
    if row["is_chat"]:
        conv = conn.execute(
            "SELECT id, title FROM conversations WHERE chat_file_id=?", (file_id,)
        ).fetchone()
        if conv:
            loc_night = conn.execute(
                "SELECT COUNT(*) FROM chat_messages WHERE conv_id=? AND mentions_location=1 AND night_hour=1",
                (conv["id"],),
            ).fetchone()[0]
            if loc_night > 0:
                add("location_night_activity", f"Location at night")
            coded = conn.execute(
                "SELECT COUNT(*) FROM chat_messages WHERE conv_id=? AND coded_marker=1",
                (conv["id"],),
            ).fetchone()[0]
            if coded > 0:
                add("coded_language", f"Coded language markers")

    # --- Bulk duplication ---
    if row["sha256"]:
        n = conn.execute(
            "SELECT COUNT(*) FROM files WHERE sha256=? AND id<>?", (row["sha256"], file_id)
        ).fetchone()[0]
        if n >= 4:  # >=5 total identical SHA-256 means n>=4 other files
            add("bulk_duplication", f"Bulk duplication")

    return fired

def create_flag(conn: sqlite3.Connection, file_id: int, fired: list[dict], explanation: str | None, explain_source: str) -> int | None:
    if not fired:
        return None
    score = min(100, sum(r["points"] for r in fired))
    severity = severity_for(score)
    cur = conn.execute(
        "INSERT INTO flags (file_id,severity,score,rule_names_json,explanation,explain_source,created_at) "
        "VALUES (?,?,?,?,?,?,?)",
        (file_id, severity, score, dbm.json_dumps([r["rule"] for r in fired]), explanation, explain_source, dbm.now_iso())
    )
    flag_id = cur.lastrowid
    for r in fired:
        conn.execute(
            "INSERT INTO rules_fired (flag_id,rule,points,detail,plain_label) VALUES (?,?,?,?,?)",
            (flag_id, r["rule"], r["points"], r["detail"], config.PLAIN_LABELS.get(r["rule"], r["rule"]))
        )
    return flag_id

def run_risk_layer(conn: sqlite3.Connection, target_path: Path, progress_cb=None) -> list[int]:
    print("\n=== [Stage] Risk Scoring & Synthetic Checks ===")
    file_ids = [r["id"] for r in conn.execute("SELECT id FROM files ORDER BY id")]
    flag_ids = []
    total = len(file_ids)
    for i, fid in enumerate(file_ids, start=1):
        fired = assess_file(conn, fid, target_path)
        if fired:
            score = min(100, sum(r["points"] for r in fired))
            print(f"  [Risk] Flagged file ID {fid} with score {score}/100. Fired {len(fired)} rule(s).")
        flag_id = create_flag(conn, fid, fired, None, "template")
        if flag_id:
            flag_ids.append(flag_id)
        if progress_cb:
            progress_cb("Scoring risk", i, total)
        conn.commit()
    return flag_ids
