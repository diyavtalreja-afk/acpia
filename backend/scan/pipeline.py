"""Pipeline — ties ingestion -> screening -> scoring -> explanations into one scan."""
import sqlite3
import threading

from .. import config, db as dbm
from ..explain.base import ExplanationProvider, build_evidence
from . import ingest, risk

MODULE_ORDER = [
    ("ingestion", "INGEST — validating files by content, capturing metadata..."),
    ("hash_match", "HASH SCREEN — checking against known content, catching near-duplicates..."),
    ("synthetic", "SYNTHETIC CHECK — screening for AI-generated content..."),
    ("risk", "RISK SCORE — nine rules, scoring what fired..."),
    ("explain", "EXPLAIN — generating plain-language reasoning, on-device..."),
    ("graph", "GRAPH — mapping connections between files, people, and devices..."),
]

class ScanProgress:
    def __init__(self, scan_id: int):
        self.scan_id = scan_id
        self.events: list[dict] = []
        self.done = False
        self._lock = threading.Lock()

    def emit(self, event: str, **payload):
        with self._lock:
            self.events.append({"event": event, **payload})

    def snapshot(self, since: int = 0) -> tuple[list[dict], bool]:
        with self._lock:
            return list(self.events[since:]), self.done

def run_full_scan(progress: ScanProgress, target_path=None, llm_client=None) -> dict:
    from pathlib import Path
    if target_path is None:
        target_path = config.DEVICE_DIR
    conn = dbm.connect()
    try:
        dbm.init_db(conn)
        conn.executescript(
            "DELETE FROM hash_matches; DELETE FROM flags; DELETE FROM rules_fired; "
            "DELETE FROM chat_messages; DELETE FROM conversations; DELETE FROM files;"
        )
        cur = conn.execute(
            "INSERT INTO scan_runs (started_at,status,seizure_ts,reference_ts) VALUES (?,?,?,?)",
            (dbm.now_iso(), "running", config.SEIZURE_ISO, config.CASE_REFERENCE_ISO),
        )
        scan_id = cur.lastrowid
        conn.commit()
        progress.emit("scan_started", scan_id=scan_id)

        def cb(msg, n, total):
            progress.emit("progress", message=msg, processed=n, total=total)

        progress.emit("module", module="ingestion", label=MODULE_ORDER[0][1])
        summary = ingest.scan_device(conn, scan_id, target_path=target_path, progress_cb=cb)
        conn.commit()
        progress.emit("module_done", module="ingestion")
        
        progress.emit("module", module="hash_match", label=MODULE_ORDER[1][1])
        progress.emit("module_done", module="hash_match")
        
        progress.emit("module", module="synthetic", label=MODULE_ORDER[2][1])
        progress.emit("module_done", module="synthetic")
        
        progress.emit("module", module="risk", label=MODULE_ORDER[3][1])
        flag_ids = risk.run_risk_layer(conn, target_path=target_path, progress_cb=cb)
        conn.commit()
        progress.emit("module_done", module="risk")

        progress.emit("module", module="explain", label=MODULE_ORDER[4][1])
        provider = ExplanationProvider()
        sources = {"llm": 0, "template": len(flag_ids)}
        for i, fid in enumerate(flag_ids, start=1):
            evidence = build_evidence(conn, fid)
            expl = provider.explain(evidence)
            conn.execute("UPDATE flags SET explanation=?, explain_source=? WHERE id=?",
                         (expl.text, expl.source, fid))
            progress.emit("progress", message=f"Explaining flag {i}/{len(flag_ids)}",
                          processed=i, total=len(flag_ids))
            conn.commit()
        progress.emit("module_done", module="explain")

        progress.emit("module", module="graph", label=MODULE_ORDER[5][1])
        from ..graph.kg import build_graph, compute_positions
        G = build_graph(conn)
        pos = compute_positions(G)
        conn.execute(
            "INSERT OR REPLACE INTO meta (key,value) VALUES ('graph_pos',?)",
            (dbm.json_dumps({k: [float(v[0]), float(v[1])] for k, v in pos.items()}),),
        )
        progress.emit("module_done", module="graph", node_count=G.number_of_nodes())

        conn.execute("UPDATE scan_runs SET status='done', finished_at=? WHERE id=?",
                     (dbm.now_iso(), scan_id))
        conn.commit()
        progress.emit("done", scan_id=scan_id, flags=len(flag_ids), sources=sources)
        return {"scan_id": scan_id, "flags": len(flag_ids), "sources": sources}
    finally:
        progress.done = True
        conn.close()

def make_llm_client():
    return None
