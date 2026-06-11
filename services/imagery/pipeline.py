"""End-to-end imagery + ML pipeline for one AOI and a pair of dates.

Produces an NDVI overlay PNG, a change overlay PNG, and a GeoJSON detection
layer. Used by the CLI and (in Phase 3) wrapped as MCP tools.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from services.ml.infer import segment
from services.ml.postprocess import mask_to_geojson

from .change import classify_change, ndvi_difference
from .ndvi import compute_ndvi
from .render import render_change, render_ndvi

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "out"


@dataclass
class PipelineResult:
    aoi: str
    bbox: list[float]
    ndvi_overlay: Path
    change_overlay: Path
    detections_geojson: Path
    detection_count: int
    coverage_fraction: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "aoi": self.aoi,
            "bbox": self.bbox,
            "ndvi_overlay": str(self.ndvi_overlay),
            "change_overlay": str(self.change_overlay),
            "detections_geojson": str(self.detections_geojson),
            "detection_count": self.detection_count,
            "coverage_fraction": self.coverage_fraction,
            "notes": self.notes,
        }


def run_pipeline(
    name: str,
    bbox: list[float],
    red_before: np.ndarray,
    nir_before: np.ndarray,
    red_after: np.ndarray,
    nir_after: np.ndarray,
    out_dir: Path = OUT_DIR,
    notes: list[str] | None = None,
) -> PipelineResult:
    """Compute NDVI, change, and vegetation detections; write artifacts."""
    out_dir.mkdir(parents=True, exist_ok=True)

    ndvi_before = compute_ndvi(red_before, nir_before)
    ndvi_after = compute_ndvi(red_after, nir_after)
    diff = ndvi_difference(ndvi_before, ndvi_after)
    change = classify_change(diff)

    mask = segment(ndvi_after)
    fc = mask_to_geojson(mask, bbox, label="vegetation")

    ndvi_png = render_ndvi(ndvi_after, out_dir / f"{name}_ndvi.png")
    change_png = render_change(change, out_dir / f"{name}_change.png")
    geojson_path = out_dir / f"{name}_detections.geojson"
    geojson_path.write_text(json.dumps(fc, indent=2))

    return PipelineResult(
        aoi=name,
        bbox=bbox,
        ndvi_overlay=ndvi_png,
        change_overlay=change_png,
        detections_geojson=geojson_path,
        detection_count=fc["properties"]["detection_count"],
        coverage_fraction=fc["properties"]["coverage_fraction"],
        notes=notes or [],
    )


def synthetic_scene(
    size: int = 256, seed: int = 0, veg_fraction: float = 0.0
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a deterministic synthetic (red, nir) pair for offline demos.

    veg_fraction grows a vegetated block so the two dates differ, exercising the
    change-detection path without any network access.
    """
    rng = np.random.default_rng(seed)
    red = rng.uniform(0.05, 0.2, size=(size, size)).astype(np.float32)
    nir = rng.uniform(0.1, 0.25, size=(size, size)).astype(np.float32)
    if veg_fraction > 0:
        span = int(size * veg_fraction)
        nir[:span, :span] = rng.uniform(0.6, 0.9, size=(span, span)).astype(np.float32)
        red[:span, :span] = rng.uniform(0.03, 0.08, size=(span, span)).astype(np.float32)
    return red, nir
