"""
ACPIA module tests — each layer verified against data/manifest.json (the
single source of truth written by the generator). Run:  pytest backend/tests -q
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend import config  # noqa: E402
from backend.scan.synthetic_check import score_image  # noqa: E402
from backend.scan.hashing import phash_distance_hex, phash_file  # noqa: E402


def load_manifest() -> dict:
    return json.loads(config.MANIFEST_FILE.read_text(encoding="utf-8"))


MANIFEST = load_manifest()


@pytest.fixture(scope="module", autouse=True)
def scanned_case():
    """One full scan before the module's tests (agent tests need data)."""
    from backend import db as dbm
    from backend.scan.pipeline import ScanProgress, run_full_scan

    conn = dbm.connect()
    dbm.init_db(conn)
    n = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    conn.close()
    if n == 0:
        run_full_scan(ScanProgress(0), llm_client=None)
    yield


# ---------------------------------------------------------------- artifact contract

def test_artifact_contract_synthetic_images():
    for s in MANIFEST["synthetic_images"]:
        sc = score_image(str(config.DEVICE_DIR / s["path"]))
        assert sc >= s["expect_score_min"], f"{s['path']}: {sc:.4f} < {s['expect_score_min']}"
        assert sc >= 0.80, f"{s['path']}: below rule threshold 0.80 ({sc:.4f})"


def test_artifact_contract_natural_controls():
    for c in MANIFEST["natural_controls"]:
        sc = score_image(str(config.DEVICE_DIR / c["path"]))
        assert sc <= c["expect_score_max"], f"{c['path']}: {sc:.4f} > {c['expect_score_max']}"


def test_artifact_determinism():
    p = config.DEVICE_DIR / "ai_generated/abstract_7.png"
    assert score_image(str(p)) == score_image(str(p))


def test_artifact_manifest_records_spec():
    for s in MANIFEST["synthetic_images"]:
        assert s["type"] == "seeded_noise"
        assert s["saved_as"] == "png"


# ---------------------------------------------------------------- hash matching

def test_phash_variants_within_threshold():
    pairs = [
        ("MOCK-0001_seed.png", "photos/IMG_4471.jpg"),
        ("MOCK-0007_seed.png", "ai_generated/scene_glitch_3.png"),
        ("MOCK-0002_seed.png", "photos/photo_similar_2.jpg"),
    ]
    for seed, variant in pairs:
        d = phash_distance_hex(
            phash_file(str(config.DATA_DIR / "known_seed" / seed)),
            phash_file(str(config.DEVICE_DIR / variant)),
        )
        assert d <= config.PHASH_THRESHOLD, f"{seed} vs {variant}: {d}"


def test_known_hashes_db_is_invented_placeholders():
    data = json.loads(config.KNOWN_HASHES_FILE.read_text(encoding="utf-8"))
    assert all(e["id"].startswith("MOCK-") for e in data["entries"])
    assert "INVENTED" in data["note"].upper()


# ---------------------------------------------------------------- full scan (pipeline)

def test_full_scan_matches_manifest():
    """Run the real pipeline; every manifest item must produce its expected rules."""
    from backend import db as dbm
    from backend.scan.pipeline import ScanProgress, run_full_scan

    dbm.reset_db()
    prog = ScanProgress(0)
    summary = run_full_scan(prog, llm_client=None)
    assert summary["flags"] >= len(MANIFEST["items"])

    conn = dbm.connect()
    try:
        # 1) every manifest item has a flag with the expected rules
        by_path = {}
        for r in conn.execute(
            "SELECT f.path, fl.id flag_id, fl.score FROM files f JOIN flags fl ON fl.file_id=f.id"
        ):
            by_path.setdefault(r["path"], []).append((r["flag_id"], r["score"]))

        for item in MANIFEST["items"]:
            assert item["path"] in by_path, f"no flag for {item['path']}"
            flag_id, score = by_path[item["path"]][0]
            rules = {r["rule"] for r in conn.execute(
                "SELECT rule FROM rules_fired WHERE flag_id=?", (flag_id,))}
            for expected_rule in item["expect"]["rules"]:
                assert expected_rule in rules, f"{item['path']}: missing rule {expected_rule}"
            if "min_score" in item["expect"]:
                assert score >= item["expect"]["min_score"], (
                    f"{item['path']}: score {score} < {item['expect']['min_score']}")

        # 2) traceability invariant: flag.score == SUM(rules_fired.points)
        bad = conn.execute(
            """SELECT fl.id FROM flags fl
               WHERE fl.score <> (SELECT COALESCE(SUM(points),0) FROM rules_fired WHERE flag_id=fl.id)
               LIMIT 5"""
        ).fetchall()
        assert not bad, f"score != sum(points) for flags {[b['id'] for b in bad]}"

        # 3) every flag has an explanation referencing its rules
        missing = conn.execute(
            "SELECT id FROM flags WHERE explanation IS NULL OR length(explanation) < 30 LIMIT 5"
        ).fetchall()
        assert not missing

        # 4) chat story: Harbour Line within last 30 days, night activity
        n_hl = conn.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE mentions_location=1 AND text LIKE '%Harbour Line%'"
        ).fetchone()[0]
        assert n_hl >= 9
        night = conn.execute(
            "SELECT sender, COUNT(*) n FROM chat_messages WHERE night_hour=1 GROUP BY sender ORDER BY n DESC"
        ).fetchall()
        assert night[0]["sender"] == "Manoj P" and night[0]["n"] >= 13

        # 5) explanations fall back to template when no LLM
        sources = {r["explain_source"] for r in conn.execute("SELECT explain_source FROM flags")}
        assert sources <= {"template"}  # no LLM key in CI => all template
    finally:
        conn.close()


# ---------------------------------------------------------------- agent queries

def test_agent_canned_queries():
    from backend import db as dbm
    from backend.agent.react import run_query

    conn = dbm.connect()
    try:
        for q in MANIFEST["queries"]:
            res = run_query(conn, q["question"], llm_client=None)
            assert res["intent"] == q["expect"]["intent"], q["question"]
            if q["expect"]["intent"] == "find_messages_mentioning":
                convs = {i["conversation"] for i in res["results"]}
                assert len(convs) >= len(q["expect"]["conversations"]), q["question"]
                assert len(res["results"]) >= q["expect"]["min_messages"]
            elif q["expect"]["intent"] == "most_active_contact":
                assert res["results"][0]["contact"] == q["expect"]["top"]
                assert res["results"][0]["count"] >= q["expect"]["min_count"]
            elif q["expect"]["intent"] == "find_files_similar_to":
                assert len(res["results"]) >= q["expect"]["min_similar"]
            assert len(res["reasoning_log"]) >= 3  # plan -> execute -> answer
            assert res["answer"]
    finally:
        conn.close()


def test_agent_reasoning_log_shape():
    from backend import db as dbm
    from backend.agent.react import run_query

    conn = dbm.connect()
    try:
        res = run_query(conn, "Show me every conversation mentioning Harbour Line in the last 30 days.")
        phases = [s["phase"] for s in res["reasoning_log"]]
        assert phases == ["plan", "execute", "answer"]
    finally:
        conn.close()


# ---------------------------------------------------------------- API

def test_api_endpoints():
    from fastapi.testclient import TestClient
    from backend import db as dbm
    from backend.main import app

    dbm.reset_db()
    from backend.scan.pipeline import ScanProgress, run_full_scan
    run_full_scan(ScanProgress(0), llm_client=None)

    client = TestClient(app)
    r = client.get("/api/case")
    assert r.status_code == 200
    body = r.json()
    assert body["mock"] is True
    assert body["files"] > 200
    assert body["flags"]["total"] >= len(MANIFEST["items"])
    assert body["risk"]["score"] > 0

    r = client.get("/api/flags")
    assert r.status_code == 200
    flags = r.json()["flags"]
    assert flags, "no flags"
    assert all(f["explanation"] for f in flags)

    r = client.get(f"/api/files/{flags[0]['file_id']}")
    assert r.status_code == 200
    assert r.json()["flags"]

    r = client.post("/api/query", json={"question": MANIFEST["queries"][0]["question"]})
    assert r.status_code == 200
    assert r.json()["answer"]

    r = client.get("/api/graph")
    assert r.status_code == 200
    g = r.json()
    assert g["node_count"] > 50
    types = {n["type"] for n in g["nodes"]}
    assert {"file", "message", "person", "location", "conversation"} <= types

    r = client.get("/api/timeline")
    assert r.status_code == 200
    kinds = {e["kind"] for e in r.json()["events"]}
    assert {"scan_started", "flag_found", "scan_done"} <= kinds

    r = client.post(f"/api/flags/{flags[0]['id']}/decision", json={"decision": "reviewed"})
    assert r.status_code == 200
    assert r.json()["ok"]


def test_case_risk_drops_after_decisions():
    from fastapi.testclient import TestClient
    from backend import db as dbm
    from backend.main import app

    dbm.reset_db()
    from backend.scan.pipeline import ScanProgress, run_full_scan
    run_full_scan(ScanProgress(0), llm_client=None)

    client = TestClient(app)
    before = client.get("/api/case").json()["risk"]["score"]
    flags = client.get("/api/flags", params={"limit": 100}).json()["flags"]
    high = [f for f in flags if f["severity"] == "high"]
    for f in high[:3]:
        client.post(f"/api/flags/{f['id']}/decision", json={"decision": "reviewed"})
    after = client.get("/api/case").json()["risk"]["score"]
    assert after < before, f"risk did not drop: {before} -> {after}"
