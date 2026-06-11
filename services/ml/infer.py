"""ONNX inference: NDVI tile in, binary vegetation mask out."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np

from .build_model import DEFAULT_MODEL_PATH, build_model


def ensure_model(path: str | Path = DEFAULT_MODEL_PATH) -> Path:
    """Build the model on first use if it is not already on disk."""
    p = Path(path)
    if not p.exists():
        build_model(p)
    return p


@lru_cache(maxsize=2)
def _session(model_path: str):
    import onnxruntime as ort

    return ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])


def segment(ndvi: np.ndarray, model_path: str | Path = DEFAULT_MODEL_PATH) -> np.ndarray:
    """Return a uint8 HxW mask (1 = vegetation) for an NDVI tile."""
    path = str(ensure_model(model_path))
    session = _session(path)
    inp = ndvi.astype(np.float32)[None, None, :, :]
    out = session.run(None, {"ndvi": inp})[0]
    return (out[0, 0] > 0.5).astype(np.uint8)
