"""Vectorize a raster mask into GeoJSON detections in WGS84 lon/lat."""

from __future__ import annotations

import numpy as np


def mask_to_geojson(
    mask: np.ndarray,
    bbox: list[float],
    label: str = "vegetation",
) -> dict:
    """Convert a binary mask to a GeoJSON FeatureCollection.

    bbox is [west, south, east, north]; the mask is assumed to cover it exactly.
    """
    from rasterio.features import shapes
    from rasterio.transform import from_bounds

    west, south, east, north = bbox
    height, width = mask.shape
    transform = from_bounds(west, south, east, north, width, height)

    binary = (mask > 0).astype(np.uint8)
    px_area = (mask == 1).sum()
    total_px = mask.size

    features = []
    for geom, value in shapes(binary, mask=binary.astype(bool), transform=transform):
        if value != 1:
            continue
        ring = geom["coordinates"][0]
        if len(ring) < 4:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": geom,
                "properties": {"label": label},
            }
        )

    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "label": label,
            "coverage_fraction": round(float(px_area) / float(total_px), 4),
            "detection_count": len(features),
        },
    }
