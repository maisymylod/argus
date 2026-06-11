"""NDVI computation. Pure numpy so it is trivially testable and dependency-light."""

from __future__ import annotations

import numpy as np


def compute_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Normalized Difference Vegetation Index = (NIR - Red) / (NIR + Red).

    Returns float32 in [-1, 1]; division-by-zero pixels map to 0.
    """
    red_f = red.astype(np.float32)
    nir_f = nir.astype(np.float32)
    denom = nir_f + red_f
    ndvi = np.divide(nir_f - red_f, denom, out=np.zeros_like(denom), where=denom != 0)
    return np.clip(ndvi, -1.0, 1.0).astype(np.float32)
