"""Render numpy arrays to RGBA PNG overlays for the map."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from .change import GAIN, LOSS


def _normalize(arr: np.ndarray, vmin: float, vmax: float) -> np.ndarray:
    scaled = (arr - vmin) / (vmax - vmin)
    return np.clip(scaled, 0.0, 1.0)


def render_ndvi(ndvi: np.ndarray, path: str | Path) -> Path:
    """Green-scale NDVI overlay. Low NDVI transparent, high NDVI opaque green."""
    t = _normalize(ndvi, -0.1, 0.8)
    h, w = ndvi.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[..., 1] = (t * 220).astype(np.uint8)  # green channel
    rgba[..., 3] = (t * 200).astype(np.uint8)  # alpha by vigor
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, mode="RGBA").save(out)
    return out


def render_change(change: np.ndarray, path: str | Path) -> Path:
    """Diverging overlay: gain=green, loss=red, none=transparent."""
    h, w = change.shape
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[change == GAIN] = (0, 200, 0, 200)
    rgba[change == LOSS] = (220, 30, 30, 200)
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, mode="RGBA").save(out)
    return out
