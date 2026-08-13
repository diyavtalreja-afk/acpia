"""
artifact_spec.py — MOCK/DEMO synthetic-media artifact contract.

Single source of truth shared by:
  - scripts/generate_mock_device.py  (PLANTS the artifact into "synthetic" images)
  - backend/scan/synthetic_check.py  (DETECTS the artifact)

Why a planted artifact? The mock device images are PIL placeholders (solid
colors, gradients, shapes). Open-ended "noise/gradient statistics" on such
images would produce arbitrary scores — there is no real synthetic-vs-real
signal to measure. So the MOCK detector works like a stand-in for a real
GAN fingerprint: the generator plants a fixed, documented artifact, and the
scorer detects exactly that artifact. Deterministic by construction.

This is NOT deepfake detection. It is a labeled MOCK/DEMO artifact detector
used to demonstrate pipeline architecture. Real synthetic-media detection
would plug a pretrained model into the same interface (see synthetic_check.py).
"""

from __future__ import annotations

import numpy as np

ARTIFACT_SEED = 42          # fixed — reproducibility
TILE = 64                   # artifact tile size in pixels (square)
ALPHA = 0.14                # blend amplitude (image values shift by ±ALPHA*0.5)
SAVE_AS = "png"             # lossless only — JPEG would add codec noise
REGION = "center"           # where the artifact is planted

# Expected score margins (asserted in tests, huge headroom by design):
#   planted images  -> score ~= 1.0  (residue ~= ALPHA * tile)
#   natural images  -> score ~= 0.0  (independent noise corr std ~= 1/sqrt(4096) ~= 0.016)
THRESHOLD_SYNTHETIC = 0.8   # score above this => "synthetic" (MOCK)
THRESHOLD_NATURAL = 0.2     # score below this => "natural" (MOCK)


def artifact_tile() -> np.ndarray:
    """Return the canonical 64x64x3 artifact tile (deterministic, cached)."""
    rng = np.random.RandomState(ARTIFACT_SEED)
    return (rng.uniform(-0.5, 0.5, size=(TILE, TILE, 3))).astype(np.float64)


_TILE_CACHE: np.ndarray | None = None


def get_tile() -> np.ndarray:
    global _TILE_CACHE
    if _TILE_CACHE is None:
        _TILE_CACHE = artifact_tile()
    return _TILE_CACHE


def plant_artifact(img: np.ndarray, alpha: float = ALPHA) -> np.ndarray:
    """Additively blend the artifact tile into the center of `img` (HxWx3 float array).

    Returns a copy with the artifact planted. Caller must clip to [0, 255]
    and save as PNG.
    """
    h, w, _ = img.shape
    y0 = (h - TILE) // 2
    x0 = (w - TILE) // 2
    out = img.copy().astype(np.float64)
    out[y0 : y0 + TILE, x0 : x0 + TILE] += alpha * get_tile()
    return out


def artifact_spec_dict(path: str) -> dict:
    """Manifest record for a planted artifact — tests read THIS, not hardcoded paths."""
    return {
        "type": "seeded_noise",
        "seed": ARTIFACT_SEED,
        "tile": TILE,
        "alpha": ALPHA,
        "region": REGION,
        "saved_as": SAVE_AS,
        "path": path,
    }
