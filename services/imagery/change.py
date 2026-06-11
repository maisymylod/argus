"""Two-date NDVI change detection."""

from __future__ import annotations

import numpy as np

# Categorical change codes used in outputs and the frontend legend.
LOSS = -1
NONE = 0
GAIN = 1


def ndvi_difference(ndvi_before: np.ndarray, ndvi_after: np.ndarray) -> np.ndarray:
    """Signed NDVI delta (after - before) as float32."""
    return (ndvi_after.astype(np.float32) - ndvi_before.astype(np.float32)).astype(np.float32)


def classify_change(diff: np.ndarray, threshold: float = 0.2) -> np.ndarray:
    """Classify each pixel as vegetation GAIN, LOSS, or NONE.

    threshold is the minimum absolute NDVI delta considered significant.
    """
    out = np.full(diff.shape, NONE, dtype=np.int8)
    out[diff >= threshold] = GAIN
    out[diff <= -threshold] = LOSS
    return out
