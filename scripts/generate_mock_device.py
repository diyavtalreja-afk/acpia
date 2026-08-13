#!/usr/bin/env python3
import hashlib
import json
import os
import random
import shutil
import sys
from datetime import datetime
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import artifact_spec, config

DEVICE = config.DEVICE_DIR
DATA = config.DATA_DIR

def make_natural(w: int, h: int, color=(100, 150, 200)) -> Image.Image:
    return Image.new("RGB", (w, h), color)

def make_synthetic(w: int, h: int, color=(200, 150, 100)) -> Image.Image:
    base = make_natural(w, h, color)
    arr = np.asarray(base, dtype=np.float64) / 255.0
    arr = artifact_spec.plant_artifact(arr)
    return Image.fromarray((np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8), "RGB")

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _phash(path: Path) -> str:
    import imagehash
    return str(imagehash.phash(Image.open(path), hash_size=16))


def touch_before_seizure(path: Path):
    old_ts = datetime(2026, 7, 31, 9, 0, 0).timestamp()
    os.utime(path, (old_ts, old_ts))

def write_chat(path: Path, msgs: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for dt, name, text in msgs:
        lines.append(f"[{dt.day:02d}/{dt.month:02d}/{dt.year % 100:02d}, {dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}] {name}: {text}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def main():
    shutil.rmtree(DEVICE, ignore_errors=True)
    DEVICE.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    
    known_entries = []
    
    # --- Images (8-10) ---
    make_natural(256, 256, (50, 50, 50)).save(DEVICE / "photo_01.png")
    make_natural(256, 256, (60, 60, 60)).save(DEVICE / "photo_02.png")
    
    # Exact-hash duplicated copies
    img3 = make_natural(256, 256, (70, 70, 70))
    img3.save(DEVICE / "photo_03.png")
    img3.save(DEVICE / "photo_03_copy.png")
    
    img4 = make_natural(256, 256, (80, 80, 80))
    img4.save(DEVICE / "photo_04.png")
    
    # Synthetic ones (seeded noise)
    make_synthetic(256, 256, (90, 90, 90)).save(DEVICE / "synthetic_01.png")
    make_synthetic(256, 256, (100, 100, 100)).save(DEVICE / "synthetic_02.png")
    make_synthetic(256, 256, (110, 110, 110)).save(DEVICE / "synthetic_03.png")
    
    # --- Register Mock Hashes ---
    known_entries.append({
        "id": "MOCK-EXACT-01",
        "label": "Exact Match",
        "sha256": _sha(DEVICE / "photo_03.png"),
        "phash": _phash(DEVICE / "photo_03.png"),
        "category": "image",
        "mock": True
    })
    
    # Create a phash variant (crop slightly for visual match but different sha)
    img4_variant = img4.crop((2, 2, 254, 254))
    temp_path = DATA / "temp_variant.png"
    img4_variant.save(temp_path)
    known_entries.append({
        "id": "MOCK-PHASH-01",
        "label": "Visual Match",
        "sha256": _sha(temp_path),
        "phash": _phash(temp_path),
        "category": "image",
        "mock": True
    })
    temp_path.unlink()
    
    # --- Chats (3-4) ---
    now = datetime.now()
    chat1 = [
        (now.replace(hour=14), "Alice", "Hello there"),
        (now.replace(hour=2), "Bob", "Are we meeting at Harbour Line?"), # location + night
        (now.replace(hour=3), "Alice", "Yes, don't forget the red package") # night + coded marker
    ]
    write_chat(DEVICE / "chat_1.txt", chat1)
    
    chat2 = [
        (now.replace(hour=10), "Charlie", "Are you going to the usual spot?"), # coded marker
        (now.replace(hour=11), "Dave", "Yes, see you soon.")
    ]
    write_chat(DEVICE / "chat_2.txt", chat2)
    
    chat3 = [
        (now.replace(hour=15), "Eve", "Normal message here"),
        (now.replace(hour=16), "Frank", "Nothing suspicious")
    ]
    write_chat(DEVICE / "chat_3.txt", chat3)
    
    # --- Mismatched extensions (1-2) ---
    make_natural(256, 256, (120, 120, 120)).save(DEVICE / "fake_zip.zip", "PNG")

    # --- Benign volume for a more realistic demo case ---
    docs = DEVICE / "documents"
    docs.mkdir(exist_ok=True)
    for i in range(1, 13):
        note = docs / f"case_note_{i:02d}.txt"
        note.write_text(
            f"Routine exported note {i:02d}. No planted risk markers in this file.\n",
            encoding="utf-8",
        )
        touch_before_seizure(note)

    logs = DEVICE / "system_logs"
    logs.mkdir(exist_ok=True)
    for i in range(1, 9):
        log = logs / f"device_log_{i:02d}.log"
        log.write_text(
            f"2026-07-31T09:{i:02d}:00+05:30 INFO Device inventory event {i:02d} recorded.\n",
            encoding="utf-8",
        )
        touch_before_seizure(log)
    
    # --- Save JSON ---
    (DATA / "mock_known_hashes.json").write_text(json.dumps({"entries": known_entries}, indent=2))
    print(f"Generated mock device with {len(list(DEVICE.rglob('*')))} files.")

if __name__ == "__main__":
    main()
