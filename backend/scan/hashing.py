"""Hashing utilities — SHA-256 (byte fingerprint) + perceptual hash (visual fingerprint)."""

from __future__ import annotations

import hashlib
import numpy as np
from PIL import Image

from .. import config


def sha256_file(path) -> str | None:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _load_image(path):
    im = Image.open(path)
    im.load()
    return im


def phash_file(path) -> str | None:
    """Perceptual hash as a 64-char hex string (16x16 DCT phash via imagehash)."""
    try:
        import imagehash

        im = _load_image(path)
        return str(imagehash.phash(im, hash_size=16))
    except Exception:
        return None


def phash_bits(hex_str: str) -> np.ndarray:
    """64-bit 0/1 array from a 16-hex-char phash string."""
    arr = np.zeros(config.PHASH_BITS, dtype=np.uint8)
    try:
        v = int(hex_str, 16)
        for i in range(config.PHASH_BITS):
            arr[i] = (v >> (config.PHASH_BITS - 1 - i)) & 1
    except ValueError:
        pass
    return arr


def phash_distance_hex(a: str, b: str) -> int:
    return int(np.count_nonzero(phash_bits(a) ^ phash_bits(b)))


def sniff_magic(path, size: int = 8) -> str:
    """Return a human-readable magic label, or None if unreadable."""
    try:
        with open(path, "rb") as f:
            head = f.read(size)
    except OSError:
        return None
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head.startswith(b"PK\x03\x04"):
        return "zip"
    if head.startswith(b"%PDF"):
        return "pdf"
    if head.startswith(b"RIFF"):
        return "riff"
    if head.startswith(b"GIF8"):
        return "gif"
    if head.startswith(b"{\"") or head.startswith(b"[{"):
        return "json"
    try:
        head.decode("utf-8")
        return "text"
    except UnicodeDecodeError:
        return "binary"
