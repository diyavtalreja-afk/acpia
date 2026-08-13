"""ACPIA configuration — all paths and constants in one place."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # acpia/
DATA_DIR = ROOT / "data"
DEVICE_DIR = ROOT / "mock_device"
KNOWN_HASHES_FILE = DATA_DIR / "mock_known_hashes.json"
MANIFEST_FILE = DATA_DIR / "manifest.json"
DB_PATH = DATA_DIR / "acpia.db"
FRONTEND_DIST = ROOT / "frontend" / "dist"

# Case clock: synthetic chats are dated relative to this fixed instant so the
# demo is deterministic regardless of when it runs.
CASE_REFERENCE_ISO = "2026-08-04T09:00:00+05:30"
SEIZURE_ISO = "2026-08-01T10:00:00+05:30"   # "device seized" moment

# Locations / contacts / markers (all invented, clearly synthetic)
LOCATIONS = [
    "Harbour Line",
    "Junction 7",
    "Meridian Point",
    "East Gate",
    "North Creek",
    "Canal Street",
]
PERSONS = [
    "Arun K",
    "Manoj P",
    "Sneha R",
    "Deepa M",
    "Vishnu T",
    "Rahul S",
]
CODED_MARKERS = ["the old library", "red package", "night shift"]

# Risk rule points (traceability: flag.score == SUM(rules_fired.points))
RULE_POINTS = {
    "hash_match_exact": 50,
    "hash_match_phash": 35,
    "synthetic_media": 25,
    "renamed_extension": 20,
    "modified_after_seizure": 20,
    "location_night_activity": 15,
    "hidden_file": 10,
    "coded_language": 10,
    "bulk_duplication": 10,
}

# Plain-language labels (Apple principle: jargon stays in the detail drawer)
PLAIN_LABELS = {
    "hash_match_exact": "Byte-identical to a known flagged file",
    "hash_match_phash": "Visually similar to a known flagged image",
    "synthetic_media": "Likely AI-generated image",
    "renamed_extension": "File disguised with a misleading filename",
    "modified_after_seizure": "Changed after the device was seized",
    "location_night_activity": "Conversation references a location during night hours",
    "hidden_file": "File hidden from normal view",
    "coded_language": "Message contains a coded-language marker",
    "bulk_duplication": "One of many identical copies",
}

SEVERITY_LOW = 40
SEVERITY_HIGH = 70

# LLM config (env-driven; absence => template fallback, demo still works)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
LLM_TIMEOUT_SECONDS = float(os.environ.get("ACPIA_LLM_TIMEOUT", "8"))
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# Scan pacing: tiny per-file delay so live progress is visible on stage.
# At ~2,300 files a 0.001s delay keeps the whole scan under ~15 s.
SCAN_DELAY_PER_FILE = float(os.environ.get("ACPIA_SCAN_DELAY", "0.001"))

# Perceptual hash match threshold (hamming distance)
PHASH_THRESHOLD = 10
PHASH_BITS = 64
