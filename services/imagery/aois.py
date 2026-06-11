"""Load sample areas of interest from data/aois/."""

from __future__ import annotations

import json
from pathlib import Path

AOIS_DIR = Path(__file__).resolve().parents[2] / "data" / "aois"


def _bbox_from_geometry(geometry: dict) -> list[float]:
    coords = geometry["coordinates"][0]
    xs = [pt[0] for pt in coords]
    ys = [pt[1] for pt in coords]
    return [min(xs), min(ys), max(xs), max(ys)]


def load_aoi(name: str, aois_dir: Path = AOIS_DIR) -> tuple[str, list[float]]:
    """Return (name, bbox=[west, south, east, north]) for a named AOI GeoJSON."""
    path = aois_dir / f"{name}.geojson"
    if not path.exists():
        available = ", ".join(sorted(p.stem for p in aois_dir.glob("*.geojson")))
        raise FileNotFoundError(f"AOI '{name}' not found. Available: {available}")
    feature = json.loads(path.read_text())
    bbox = feature.get("bbox") or _bbox_from_geometry(feature["geometry"])
    label = feature.get("properties", {}).get("name", name)
    return label, [float(v) for v in bbox]
