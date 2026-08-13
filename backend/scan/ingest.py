"""Ingestion: walk the seized-device folder, extract metadata + hashes, parse chats, write SQLite."""

from __future__ import annotations

import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import config, db as dbm
from . import hashing
from .hash_match import match_file, store_matches

WHATSAPP_RE = re.compile(
    r"^\[(\d{2})/(\d{2})/(\d{2}), (\d{2}):(\d{2}):(\d{2})\] (.*?): (.*)$"
)

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
CHAT_EXTS = {".txt", ".log"}


def is_hidden(name: str) -> bool:
    return (
        name.startswith(".")
        or name.startswith("._")
        or name in ("Thumbs.db", "Desktop.ini")
        or name.endswith("~")
    )


def _parse_chat_ts(d, mo, yy, h, mi, s) -> str:
    year = 2000 + int(yy)
    dt = datetime(int(year), int(mo), int(d), int(h), int(mi), int(s))
    # Synthetic chats are in IST (+05:30)
    return dt.isoformat(timespec="seconds") + "+05:30"


def parse_chat_file(path: Path) -> list[dict]:
    """Parse a WhatsApp-style export -> list of {sender, ts, text}."""
    messages = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return messages
    for line in text.splitlines():
        m = WHATSAPP_RE.match(line.strip())
        if not m:
            continue
        d, mo, yy, h, mi, s, sender, body = m.groups()
        ts = _parse_chat_ts(d, mo, yy, h, mi, s)
        messages.append({"sender": sender.strip(), "ts": ts, "text": body.strip()})
    return messages


def _fingerprint(p: Path, device_root: Path) -> dict:
    """One file's worth of metadata + hashes (runs in a worker thread)."""
    t0 = time.time()
    rel = p.relative_to(device_root).as_posix()
    name = p.name
    ext = p.suffix.lower()
    try:
        st = p.stat()
        modified_ts = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(timespec="seconds")
        created_ts = datetime.fromtimestamp(st.st_ctime, tz=timezone.utc).isoformat(timespec="seconds")
        size = st.st_size
    except OSError:
        modified_ts = created_ts = ""
        size = 0
    chats: list[dict] = []
    if ext in CHAT_EXTS and name.startswith("chat_"):
        chats = parse_chat_file(p)
    sha = hashing.sha256_file(p)
    phash = hashing.phash_file(p) if ext in IMAGE_EXTS else None
    magic = hashing.sniff_magic(p)
    elapsed = int((time.time() - t0) * 1000)
    print(f"  [Ingest] {name} | sha256:{sha[:8]} | phash:{phash or '-'} | {elapsed}ms")
    return {
        "rel": rel, "name": name, "ext": ext, "size": size,
        "created": created_ts, "modified": modified_ts,
        "sha": sha,
        "phash": phash,
        "magic": magic,
        "chats": chats,
    }


def scan_device(
    conn: sqlite3.Connection,
    scan_id: int,
    target_path: Path,
    progress_cb=None,
) -> dict:
    """Ingest everything under target_path. Returns summary counts."""
    from concurrent.futures import ThreadPoolExecutor

    device_root = target_path
    print(f"=== [Stage] Ingesting files from {device_root} ===")

    def progress(msg: str, n: int = 0, total: int = 0):
        if progress_cb:
            progress_cb(msg, n, total)

    paths = sorted(p for p in device_root.rglob("*") if p.is_file())
    total = len(paths)
    conn.execute(
        "UPDATE scan_runs SET files_total=?, status='running' WHERE id=?",
        (total, scan_id),
    )
    conn.commit()
    progress("Fingerprinting files (SHA-256 + perceptual hash)", 0, total)

    # ---- phase A: fingerprint in parallel (hashing dominates at 2k+ files) ----
    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for i, res in enumerate(ex.map(lambda p: _fingerprint(p, device_root), paths), start=1):
            rows.append(res)
            if i % 25 == 0:
                progress("Fingerprinting files", i, total)

    files_seen = 0
    image_rows = []  # (file_id, phash) for later similarity
    file_ids_by_path: dict[str, int] = {}

    for idx, r in enumerate(rows, start=1):
        rel, name, ext = r["rel"], r["name"], r["ext"]
        modified_ts, created_ts = r["modified"], r["created"]
        sha, phash, magic = r["sha"], r["phash"], r["magic"]
        chat_messages = r["chats"]
        is_chat = 1 if chat_messages else 0

        cur = conn.execute(
            "INSERT INTO files (path,name,ext,size_bytes,created_ts,modified_ts,"
            "sha256,phash,is_image,is_chat,is_hidden,magic,scan_run_id) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                rel,
                name,
                ext,
                r["size"],
                created_ts,
                modified_ts,
                sha,
                phash,
                1 if ext in IMAGE_EXTS else 0,
                is_chat,
                1 if is_hidden(name) else 0,
                magic,
                scan_id,
            ),
        )
        file_id = cur.lastrowid
        file_ids_by_path[rel] = file_id
        files_seen += 1

        # hash matching (mock DB)
        matches = match_file(sha, phash)
        if matches:
            print(f"  [Screen] {name} matched {len(matches)} known hash(es)")
        store_matches(conn, file_id, matches)

        # chats
        if chat_messages:
            title = name[len("chat_") : -len(ext)]
            participants = sorted({m["sender"] for m in chat_messages})
            cur = conn.execute(
                "INSERT INTO conversations (title,channel,contact,chat_file_id,participants,msg_count) "
                "VALUES (?,?,?,?,?,?)",
                (title, "whatsapp", participants[0] if participants else None, file_id,
                 dbm.json_dumps(participants), len(chat_messages)),
            )
            conv_id = cur.lastrowid
            for m in chat_messages:
                lower = m["text"].lower()
                loc = next(
                    (L for L in config.LOCATIONS if L.lower() in lower), None
                )
                coded = next(
                    (mk for mk in config.CODED_MARKERS if mk in lower), None
                )
                hour = int(m["ts"][11:13])
                conn.execute(
                    "INSERT INTO chat_messages (conv_id,sender,ts,text,mentions_location,"
                    "coded_marker,night_hour) VALUES (?,?,?,?,?,?,?)",
                    (
                        conv_id,
                        m["sender"],
                        m["ts"],
                        m["text"][:2000],
                        1 if loc else 0,
                        1 if coded else 0,
                        1 if 0 <= hour < 4 else 0,
                    ),
                )

        if phash:
            image_rows.append((file_id, phash))

        conn.execute(
            "UPDATE scan_runs SET files_processed=? WHERE id=?", (files_seen, scan_id)
        )
        conn.commit()
        progress(f"Processing {name}", files_seen, total)
        time.sleep(config.SCAN_DELAY_PER_FILE)  # visible pacing for the live demo

    # intra-device perceptual near-duplicates (for 'similar to' queries + graph edges)
    similar_edges = _pairwise_similar(image_rows)
    for a, b, dist in similar_edges:
        conn.execute(
            "INSERT INTO hash_matches (file_id, hash_type, known_id, confidence, distance) "
            "VALUES (?,?,?,?,?)",
            (a, "similar_to", f"FILE-{b}", round(1 - dist / 64, 3), dist),
        )

    conn.execute(
        "UPDATE scan_runs SET status='done', finished_at=? WHERE id=?",
        (dbm.now_iso(), scan_id),
    )
    conn.commit()
    return {"files": files_seen, "images": len(image_rows)}


def _pairwise_similar(image_rows: list[tuple[int, str]], threshold: int = 10):
    """Find image pairs whose phash distance <= threshold (bounded fan-out)."""
    from .hashing import phash_bits

    if len(image_rows) > 1200:  # safety cap
        return []
    bits = [(fid, phash_bits(h)) for fid, h in image_rows]
    out = []
    for i in range(len(bits)):
        fid_i, b_i = bits[i]
        for j in range(i + 1, len(bits)):
            fid_j, b_j = bits[j]
            dist = int((b_i ^ b_j).sum())
            if dist <= threshold:
                out.append((fid_i, fid_j, dist))
    return out
