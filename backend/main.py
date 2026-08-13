from __future__ import annotations

import asyncio
import json
import threading
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from . import config, db as dbm
from .agent.react import run_query
from .agent.tools import get_graph
from .scan.pipeline import ScanProgress, run_full_scan

app = FastAPI(title="ACPIA", version="0.1.0-mock")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_scans: dict[int, ScanProgress] = {}
_scan_lock = threading.Lock()

def _conn():
    conn = dbm.connect()
    dbm.init_db(conn)
    return conn

def _case_risk(conn) -> dict:
    row = conn.execute(
        """SELECT COUNT(*) n, COALESCE(MAX(score),0) mx,
                  COALESCE(SUM(score),0) total,
                  SUM(CASE WHEN severity='high' THEN 1 ELSE 0 END) high
           FROM flags"""
    ).fetchone()
    n = row["n"]
    if n == 0:
        return {"score": 0, "label": "SAFE", "flags_open": 0}
    top3 = conn.execute("SELECT score FROM flags ORDER BY score DESC LIMIT 3").fetchall()
    avg3 = sum(r["score"] for r in top3) / 3.0
    raw = row["mx"] * 0.55 + avg3 * 0.12 + n * 0.55 + (row["high"] or 0) * 3.5
    score = min(100, round(raw))
    label = "SAFE" if score < 40 else ("REVIEW" if score < 70 else "HIGH RISK")
    return {"score": score, "label": label, "flags_open": n}

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/case")
def case_overview():
    conn = _conn()
    try:
        files = conn.execute("SELECT COUNT(*) n, SUM(is_image) imgs, SUM(is_chat) chats, SUM(is_hidden) hidden FROM files").fetchone()
        flags = conn.execute("SELECT COUNT(*) n, SUM(CASE WHEN severity='high' THEN 1 ELSE 0 END) h, SUM(CASE WHEN severity='medium' THEN 1 ELSE 0 END) m, SUM(CASE WHEN severity='low' THEN 1 ELSE 0 END) l FROM flags").fetchone()
        last_scan = conn.execute("SELECT * FROM scan_runs ORDER BY id DESC LIMIT 1").fetchone()
        return {
            "files": files["n"] or 0,
            "flags": {"total": flags["n"] or 0, "high": flags["h"] or 0, "medium": flags["m"] or 0, "low": flags["l"] or 0},
            "risk": _case_risk(conn),
            "last_scan": dict(last_scan) if last_scan else None,
        }
    finally:
        conn.close()

class ScanRequest(BaseModel):
    path: str = "mock_device"

class QueryBody(BaseModel):
    question: str

@app.post("/api/scan")
def start_scan(req: ScanRequest):
    conn = _conn()
    conn.close()
    prog = ScanProgress(0)
    with _scan_lock:
        scan_id = len(_scans) + 1
        prog.scan_id = scan_id
        _scans[scan_id] = prog
        
    target_path = Path(req.path)
    if not target_path.is_absolute():
        target_path = (Path(__file__).parent.parent / req.path).absolute()
        
    print(f"\n\n*** [API] Starting scan on path: {target_path} ***")
    thread = threading.Thread(target=run_full_scan, args=(prog, target_path), daemon=True)
    thread.start()
    return {"scan_id": scan_id, "status": "started"}

@app.get("/api/scan/events")
async def scan_events(scan_id: int):
    prog = _scans.get(scan_id)
    if prog is None:
        raise HTTPException(404, "unknown scan")
    async def gen():
        since = 0
        while True:
            events, done = prog.snapshot(since)
            since += len(events)
            for e in events:
                yield f"data: {json.dumps(e)}\n\n"
            if done:
                yield "event: done\ndata: {}\n\n"
                return
            await asyncio.sleep(0.15)
    return StreamingResponse(gen(), media_type="text/event-stream")

@app.get("/api/flags")
def list_flags():
    conn = _conn()
    try:
        q = """SELECT fl.id, fl.file_id, fl.severity, fl.score, fl.explanation,
                      f.name, f.path
               FROM flags fl JOIN files f ON f.id = fl.file_id ORDER BY fl.score DESC LIMIT 50"""
        rows = conn.execute(q).fetchall()
        flags = []
        for r in rows:
            d = dict(r)
            rules = conn.execute("SELECT rule, points, detail, plain_label FROM rules_fired WHERE flag_id=?", (d["id"],)).fetchall()
            d["rules"] = [dict(rule) for rule in rules]
            flags.append(d)
        return {"flags": flags}
    finally:
        conn.close()

@app.post("/api/query")
def query(body: QueryBody):
    if not body.question.strip():
        raise HTTPException(400, "empty question")
    conn = _conn()
    try:
        return run_query(conn, body.question, None)
    finally:
        conn.close()

@app.get("/api/graph")
def graph(focus: str | None = None, depth: int = 2):
    conn = _conn()
    try:
        meta = conn.execute("SELECT value FROM meta WHERE key='graph_pos'").fetchone()
        pos = {k: tuple(v) for k, v in dbm.json_loads(meta["value"]).items()} if meta else None
        return get_graph(conn, focus=focus, depth=depth, pos=pos)
    finally:
        conn.close()

@app.post("/api/case/new")
def new_case():
    dbm.reset_db()
    return {"ok": True}

@app.get("/")
def index():
    dist = config.FRONTEND_DIST
    if (dist / "index.html").exists():
        return FileResponse(dist / "index.html")
    return {"message": "Frontend not built yet"}

@app.get("/{path:path}")
def spa(path: str):
    dist = config.FRONTEND_DIST
    candidate = (dist / path)
    if candidate.is_file():
        return FileResponse(candidate)
    if (dist / "index.html").exists() and not path.startswith("api/"):
        return FileResponse(dist / "index.html")
    raise HTTPException(404, "not found")
