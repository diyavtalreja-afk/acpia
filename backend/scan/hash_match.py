"""Hash-match layer: compare device files against the mock known-hash DB.

MOCK/DEMO: the known-hash DB (mock_known_hashes.json) contains invented
placeholder hashes only. Real known-material hash databases (NCMEC, PhotoDNA,
ICSE) are restricted-access for good reason — this prototype never uses or
simulates them.
"""

from __future__ import annotations

import json
import sqlite3

from .. import config
from . import hashing

_known_cache: dict | None = None


def load_known_hashes() -> dict:
    global _known_cache
    if _known_cache is None:
        with open(config.KNOWN_HASHES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _known_cache = data
    return _known_cache


def reset_cache() -> None:
    global _known_cache
    _known_cache = None


def _known_index() -> tuple[dict[str, dict], dict[str, dict]]:
    """Index entries by sha256 and by phash -> (by_sha, by_phash)."""
    data = load_known_hashes()
    by_sha = {}
    by_phash = {}
    for e in data["entries"]:
        if e.get("sha256"):
            by_sha[e["sha256"]] = e
        if e.get("phash"):
            by_phash.setdefault(e["phash"], []).append(e)
    return by_sha, by_phash


def match_file(sha256: str | None, phash: str | None) -> list[dict]:
    """Return match dicts for one file: [{hash_type, known_id, confidence, distance}]."""
    out = []
    if not sha256 and not phash:
        return out
    by_sha, by_phash = _known_index()

    if sha256 and sha256 in by_sha:
        e = by_sha[sha256]
        out.append(
            {
                "hash_type": "sha256",
                "known_id": e["id"],
                "confidence": 1.0,
                "distance": 0,
            }
        )

    if phash:
        from .hashing import phash_bits

        my_bits = phash_bits(phash)
        best: tuple[int, dict | None] = (10_000, None)
        for known_phash, entries in by_phash.items():
            dist = int((phash_bits(known_phash) ^ my_bits).sum())
            if dist < best[0]:
                best = (dist, entries[0])
        dist, entry = best
        if entry is not None and dist <= config.PHASH_THRESHOLD:
            out.append(
                {
                    "hash_type": "phash",
                    "known_id": entry["id"],
                    "confidence": round(1.0 - dist / config.PHASH_BITS, 3),
                    "distance": dist,
                }
            )
    return out


def store_matches(conn: sqlite3.Connection, file_id: int, matches: list[dict]) -> None:
    for m in matches:
        conn.execute(
            "INSERT INTO hash_matches (file_id, hash_type, known_id, confidence, distance) "
            "VALUES (?,?,?,?,?)",
            (file_id, m["hash_type"], m["known_id"], m["confidence"], m["distance"]),
        )
