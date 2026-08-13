#!/usr/bin/env python3
"""
generate_mock_device.py — Builds the 146-file mock device dataset + known-hash DB.

Generates the complete digital-forensics mock device structure described in README.md:
  - 38 images (natural controls + synthetic media + phash/exact matches)
  - 60 documents (case notes, work files, photoburst logs)
  - 20 data files (system logs, data archives)
  - 12 PDFs (scanned documents)
  - 12 audio clips (voice notes)
  - 4 chat exports (arun_manoj, sneha_deepa, etc.)
Total files: 146 files.
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend import artifact_spec, config

DEVICE = config.DEVICE_DIR
DATA = config.DATA_DIR
KNOWN_SEED = DATA / "known_seed"

# Keep the demo responsive while retaining enough benign volume for triage.
TARGET_IMAGES = 36  # photos + AI-generated images; two additional images live in data/
TARGET_DOCUMENTS = 60
TARGET_DATA_FILES = 20
TARGET_PDFS = 12
TARGET_AUDIO_CLIPS = 12


def make_natural(w: int, h: int, color=(100, 150, 200)) -> Image.Image:
    return Image.new("RGB", (w, h), color)

def make_pattern_img(w: int, h: int, seed: int) -> Image.Image:
    rng = np.random.RandomState(seed)
    # Smooth gradient + noise for stable perceptual hash matching
    x = np.linspace(0, 255, w)
    y = np.linspace(0, 255, h)
    xx, yy = np.meshgrid(x, y)
    r = (xx + yy) / 2.0 + rng.uniform(-10, 10, (h, w))
    g = xx + rng.uniform(-10, 10, (h, w))
    b = yy + rng.uniform(-10, 10, (h, w))
    arr = np.stack([r, g, b], axis=-1)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def make_synthetic(base_img: Image.Image, alpha: float = artifact_spec.ALPHA) -> Image.Image:
    arr = np.asarray(base_img, dtype=np.float64) / 255.0
    arr = artifact_spec.plant_artifact(arr, alpha=alpha)
    return Image.fromarray((np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8), "RGB")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _phash(path: Path) -> str:
    import imagehash
    return str(imagehash.phash(Image.open(path), hash_size=16))


def touch_before_seizure(path: Path, days_before: int = 2):
    seizure_dt = datetime.fromisoformat(config.SEIZURE_ISO.replace("Z", "+00:00"))
    old_ts = (seizure_dt - timedelta(days=days_before)).timestamp()
    os.utime(path, (old_ts, old_ts))


def touch_after_seizure(path: Path, days_after: int = 1):
    seizure_dt = datetime.fromisoformat(config.SEIZURE_ISO.replace("Z", "+00:00"))
    new_ts = (seizure_dt + timedelta(days=days_after)).timestamp()
    os.utime(path, (new_ts, new_ts))


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
    KNOWN_SEED.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------- 1. Seed & Known Hashes
    # Seed 1: MOCK-0001 (IMG_4471.jpg phash match)
    seed1_img = make_pattern_img(256, 256, seed=101)
    seed1_path = KNOWN_SEED / "MOCK-0001_seed.png"
    seed1_img.save(seed1_path)

    # Seed 2: MOCK-0002 (photo_similar_2.jpg phash match)
    seed2_img = make_pattern_img(256, 256, seed=202)
    seed2_path = KNOWN_SEED / "MOCK-0002_seed.png"
    seed2_img.save(seed2_path)

    # Seed 7: MOCK-0007 (scene_glitch_3.png phash match)
    seed7_base = make_pattern_img(256, 256, seed=707)
    seed7_img = make_synthetic(seed7_base)
    seed7_path = KNOWN_SEED / "MOCK-0007_seed.png"
    seed7_img.save(seed7_path)

    # Exact seed image for holiday_photo
    exact_img = make_natural(256, 256, (200, 100, 50))
    exact_temp = DATA / "temp_exact.png"
    exact_img.save(exact_temp)
    exact_sha = _sha(exact_temp)
    exact_phash = _phash(exact_temp)
    exact_temp.unlink()

    # Exact seed image for scene_glitch_original
    synth_exact_img = make_synthetic(make_natural(256, 256, (90, 90, 90)))
    synth_exact_temp = DATA / "temp_synth_exact.png"
    synth_exact_img.save(synth_exact_temp)
    synth_exact_sha = _sha(synth_exact_temp)
    synth_exact_phash = _phash(synth_exact_temp)
    synth_exact_temp.unlink()

    known_entries = [
        {
            "id": "MOCK-0001",
            "label": "MOCK Known CSAM Match #1",
            "sha256": _sha(seed1_path),
            "phash": _phash(seed1_path),
            "category": "image",
            "mock": True
        },
        {
            "id": "MOCK-0002",
            "label": "MOCK Known CSAM Match #2",
            "sha256": _sha(seed2_path),
            "phash": _phash(seed2_path),
            "category": "image",
            "mock": True
        },
        {
            "id": "MOCK-0007",
            "label": "MOCK Known CSAM Match #7",
            "sha256": _sha(seed7_path),
            "phash": _phash(seed7_path),
            "category": "image",
            "mock": True
        },
        {
            "id": "MOCK-EXACT-HOLIDAY",
            "label": "MOCK Exact Match Holiday",
            "sha256": exact_sha,
            "phash": exact_phash,
            "category": "image",
            "mock": True
        },
        {
            "id": "MOCK-EXACT-SYNTH",
            "label": "MOCK Exact Match Synth",
            "sha256": synth_exact_sha,
            "phash": synth_exact_phash,
            "category": "image",
            "mock": True
        }
    ]

    known_db = {
        "note": "MOCK/DEMO INVENTED PLACEHOLDER HASHES ONLY - NEVER REAL HASHES",
        "entries": known_entries
    }
    (DATA / "mock_known_hashes.json").write_text(json.dumps(known_db, indent=2), encoding="utf-8")

    # --------------------------------------------------------- 2. Manifest Items
    photos_dir = DEVICE / "photos"
    photos_dir.mkdir(parents=True, exist_ok=True)
    ai_dir = DEVICE / "ai_generated"
    ai_dir.mkdir(parents=True, exist_ok=True)
    data_dir = DEVICE / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # exact match + renamed extension
    holiday_path = photos_dir / "holiday_photo.jpg"
    exact_img.save(holiday_path, "PNG")  # PNG content in .jpg => renamed_extension
    touch_before_seizure(holiday_path)

    vacation_path = photos_dir / "vacation_2.jpg"
    exact_img.save(vacation_path, "PNG")  # PNG content in .jpg => renamed_extension
    touch_before_seizure(vacation_path)

    # phash match + modified after seizure
    img4471_path = photos_dir / "IMG_4471.jpg"
    seed1_img.save(img4471_path, "PNG")
    touch_after_seizure(img4471_path)

    sim2_path = photos_dir / "photo_similar_2.jpg"
    seed2_img.save(sim2_path, "PNG")
    touch_after_seizure(sim2_path)

    # synthetic + phash match + modified after seizure
    sg3_path = ai_dir / "scene_glitch_3.png"
    make_synthetic(seed7_img).save(sg3_path)
    touch_after_seizure(sg3_path)

    # synthetic + exact match
    sg_orig = ai_dir / "scene_glitch_original.png"
    synth_exact_img.save(sg_orig)
    touch_before_seizure(sg_orig)

    # synthetic + modified after seizure
    ab7_path = ai_dir / "abstract_7.png"
    make_synthetic(make_natural(256, 256, (50, 100, 150))).save(ab7_path)
    touch_after_seizure(ab7_path)

    # synthetic media (photos/random_1.png)
    rand1_path = photos_dir / "random_1.png"
    make_synthetic(make_natural(256, 256, (60, 110, 160))).save(rand1_path)
    touch_before_seizure(rand1_path)

    # synthetic media (gen_art_01, gen_art_05)
    ga1_path = ai_dir / "gen_art_01.png"
    make_synthetic(make_natural(256, 256, (70, 120, 170))).save(ga1_path)
    touch_before_seizure(ga1_path)

    ga5_path = ai_dir / "gen_art_05.png"
    make_synthetic(make_natural(256, 256, (80, 130, 180))).save(ga5_path)
    touch_before_seizure(ga5_path)

    # renamed extension + modified after seizure
    arch_back = data_dir / "archive_backup.jpg"
    make_natural(256, 256, (200, 200, 200)).save(arch_back, "PNG")
    touch_after_seizure(arch_back)

    notes_back = data_dir / "notes_backup.png"
    make_natural(256, 256, (210, 210, 210)).save(notes_back, "JPEG")
    touch_before_seizure(notes_back)

    # natural controls
    p000 = photos_dir / "photo_000.png"
    make_natural(256, 256, (10, 20, 30)).save(p000)
    touch_before_seizure(p000)

    p010 = photos_dir / "photo_010.jpg"
    make_natural(256, 256, (20, 30, 40)).save(p010, "JPEG")
    touch_before_seizure(p010)

    pb_dir = DEVICE / "documents" / "photoburst"
    pb_dir.mkdir(parents=True, exist_ok=True)
    dsc0001 = pb_dir / "DSC_0001.jpg"
    make_natural(256, 256, (30, 40, 50)).save(dsc0001, "JPEG")
    touch_before_seizure(dsc0001)

    pdfs_dir = DEVICE / "pdfs"
    pdfs_dir.mkdir(parents=True, exist_ok=True)
    scan0001 = pdfs_dir / "scan_0001.pdf"
    scan0001.write_bytes(b"%PDF-1.4 %EOF\n")
    touch_before_seizure(scan0001)

    # --------------------------------------------------------- 3. Chats (Harbour Line & Manoj P)
    chats_dir = DEVICE / "chats"
    chats_dir.mkdir(parents=True, exist_ok=True)
    now = datetime(2026, 7, 28, 10, 0, 0)

    # chat 1: chat_arun_manoj.txt (Harbour Line + Manoj P night messages)
    msgs_am = []
    # 6 Harbour Line messages
    for i in range(6):
        msgs_am.append((now.replace(hour=14, minute=i), "Arun K", f"Discussing Harbour Line meeting spot #{i+1}."))
    # 14 Manoj P night messages (00:00 - 04:00)
    for i in range(14):
        msgs_am.append((now.replace(hour=1 + (i % 3), minute=i), "Manoj P", f"Night operational update message #{i+1}."))
    write_chat(chats_dir / "chat_arun_manoj.txt", msgs_am)
    touch_before_seizure(chats_dir / "chat_arun_manoj.txt")

    # chat 2: chat_sneha_deepa.txt (5 Harbour Line messages)
    msgs_sd = []
    for i in range(5):
        msgs_sd.append((now.replace(hour=15, minute=i), "Sneha", f"Coordinates near Harbour Line station #{i+1}."))
    msgs_sd.append((now.replace(hour=16), "Deepa", "Confirmed."))
    write_chat(chats_dir / "chat_sneha_deepa.txt", msgs_sd)
    touch_before_seizure(chats_dir / "chat_sneha_deepa.txt")

    # chat 3 & 4 (additional chat exports)
    write_chat(chats_dir / "chat_group_ops.txt", [(now, "UserA", "General chatter.")])
    touch_before_seizure(chats_dir / "chat_group_ops.txt")

    write_chat(chats_dir / "chat_archive.txt", [(now, "UserB", "Archived messages.")])
    touch_before_seizure(chats_dir / "chat_archive.txt")

    # --------------------------------------------------------- 4. Scale to a compact 146-file demo dataset
    # Fast dummy PNG bytes
    dummy_img = make_natural(32, 32, (128, 128, 128))
    img_byte_arr = Path(DATA / "dummy.png")
    dummy_img.save(img_byte_arr, "PNG")
    png_bytes = img_byte_arr.read_bytes()
    img_byte_arr.unlink()

    # Target counts:
    # 36 photos/AI images + 2 images in data/ = 38 images total.
    existing_imgs = len(list(photos_dir.glob("*"))) + len(list(ai_dir.glob("*")))
    needed_imgs = max(0, TARGET_IMAGES - existing_imgs)
    for i in range(needed_imgs):
        p = photos_dir / f"photo_bulk_{i:04d}.png"
        p.write_bytes(png_bytes)
        touch_before_seizure(p)

    # 60 documents total:
    docs_dir = DEVICE / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)
    existing_docs = sum(1 for path in docs_dir.rglob("*") if path.is_file())
    needed_docs = max(0, TARGET_DOCUMENTS - existing_docs)
    for i in range(needed_docs):
        p = docs_dir / f"doc_{i:04d}.txt"
        p.write_text(f"Benign document content #{i:04d}.\n", encoding="utf-8")
        touch_before_seizure(p)

    # 20 data files:
    data_files_dir = DEVICE / "data_files"
    data_files_dir.mkdir(parents=True, exist_ok=True)
    for i in range(TARGET_DATA_FILES):
        p = data_files_dir / f"data_{i:04d}.dat"
        p.write_bytes(b"DATA_FILE_BINARY_HEADER_PLACEHOLDER\n")
        touch_before_seizure(p)

    # 12 PDFs:
    existing_pdfs = len(list(pdfs_dir.glob("*")))
    needed_pdfs = max(0, TARGET_PDFS - existing_pdfs)
    for i in range(needed_pdfs):
        p = pdfs_dir / f"scan_{i + 2:04d}.pdf"
        p.write_bytes(b"%PDF-1.4 %EOF\n")
        touch_before_seizure(p)

    # 12 audio clips:
    audio_dir = DEVICE / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    for i in range(TARGET_AUDIO_CLIPS):
        p = audio_dir / f"audio_note_{i:02d}.wav"
        p.write_bytes(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00")
        touch_before_seizure(p)

    total_files = len([f for f in DEVICE.rglob("*") if f.is_file()])
    print(f"Successfully generated full mock device with {total_files} files.")


if __name__ == "__main__":
    main()
