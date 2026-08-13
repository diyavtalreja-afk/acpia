import numpy as np
from PIL import Image
from .. import artifact_spec as spec

def _high_pass_residue(img: np.ndarray) -> np.ndarray:
    from numpy.lib.stride_tricks import sliding_window_view
    local_mean = np.empty_like(img)
    for c in range(3):
        w = sliding_window_view(img[:, :, c], (3, 3))
        local_mean[:, :, c] = np.pad(w.mean(axis=(2, 3)), 1, mode="edge")
    return img - local_mean

def _norm_corr(a: np.ndarray, b: np.ndarray) -> float:
    a = a.ravel()
    b = b.ravel()
    denom = np.sqrt(float(np.dot(a, a)) * float(np.dot(b, b)))
    if denom == 0:
        return 0.0
    return float(np.clip(np.dot(a, b) / denom, 0.0, 1.0))

def score_image(path) -> float:
    try:
        im = Image.open(path).convert("RGB")
        arr = np.asarray(im, dtype=np.float64) / 255.0
    except Exception:
        return 0.0

    h, w, _ = arr.shape
    if h < spec.TILE or w < spec.TILE:
        return 0.0

    y0 = (h - spec.TILE) // 2
    x0 = (w - spec.TILE) // 2
    region = arr[y0 : y0 + spec.TILE, x0 : x0 + spec.TILE]
    residue = _high_pass_residue(region)
    return _norm_corr(residue, spec.get_tile())
