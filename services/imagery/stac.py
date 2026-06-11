"""Public STAC search and windowed band reads (Microsoft Planetary Computer).

Network-dependent; unit tests cover the pure logic and mark live STAC calls as
integration. Public Sentinel-2 L2A only (see README data policy).
"""

from __future__ import annotations

import numpy as np

# Sentinel-2 L2A asset keys on Planetary Computer.
RED_BAND = "B04"
NIR_BAND = "B08"


def open_catalog(stac_url: str):
    """Open a STAC catalog, signing asset hrefs for Planetary Computer."""
    import planetary_computer as pc
    from pystac_client import Client

    return Client.open(stac_url, modifier=pc.sign_inplace)


def search_least_cloudy(
    catalog,
    bbox: list[float],
    date_range: tuple[str, str],
    collection: str = "sentinel-2-l2a",
    max_cloud: float = 20.0,
):
    """Return the least-cloudy item in the bbox and date window, or None."""
    search = catalog.search(
        collections=[collection],
        bbox=bbox,
        datetime=f"{date_range[0]}/{date_range[1]}",
        query={"eo:cloud_cover": {"lt": max_cloud}},
    )
    items = list(search.items())
    if not items:
        return None
    return min(items, key=lambda it: it.properties.get("eo:cloud_cover", 100.0))


def read_band(item, band: str, bbox: list[float], out_size: int = 256) -> np.ndarray:
    """Read a band windowed to bbox (WGS84) at out_size x out_size."""
    import rasterio
    from rasterio.warp import transform_bounds
    from rasterio.windows import from_bounds

    href = item.assets[band].href
    with rasterio.open(href) as ds:
        left, bottom, right, top = transform_bounds("EPSG:4326", ds.crs, *bbox)
        window = from_bounds(left, bottom, right, top, ds.transform)
        return ds.read(1, window=window, out_shape=(out_size, out_size)).astype(np.float32)


def read_red_nir(item, bbox: list[float], out_size: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Convenience: read the red and NIR bands for NDVI."""
    return (
        read_band(item, RED_BAND, bbox, out_size),
        read_band(item, NIR_BAND, bbox, out_size),
    )
