"""CLI: python -m services.imagery --aoi <name> --before <date> --after <date> [--demo]

Produces an NDVI overlay PNG, change overlay PNG, and GeoJSON detections under
data/out/. With --demo it runs fully offline on synthetic scenes; otherwise it
fetches public Sentinel-2 imagery from the configured STAC API.
"""

from __future__ import annotations

import argparse
import os
import sys

from .aois import load_aoi
from .pipeline import run_pipeline, synthetic_scene


def _fetch_real(bbox, before, after, out_size):
    from .stac import open_catalog, read_red_nir, search_least_cloudy

    stac_url = os.environ.get("STAC_URL", "https://planetarycomputer.microsoft.com/api/stac/v1")
    catalog = open_catalog(stac_url)
    notes = []
    pairs = {}
    for key, (d0, d1) in {"before": before, "after": after}.items():
        item = search_least_cloudy(catalog, bbox, (d0, d1))
        if item is None:
            raise SystemExit(f"No cloud-free scene found for {key} window {d0}/{d1}")
        notes.append(f"{key}: {item.id} (cloud {item.properties.get('eo:cloud_cover', '?')}%)")
        pairs[key] = read_red_nir(item, bbox, out_size)
    (rb, nb), (ra, na) = pairs["before"], pairs["after"]
    return rb, nb, ra, na, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="services.imagery")
    parser.add_argument("--aoi", required=True, help="AOI name under data/aois/")
    parser.add_argument("--before", required=True, help="before date YYYY-MM-DD")
    parser.add_argument("--after", required=True, help="after date YYYY-MM-DD")
    parser.add_argument("--window", type=int, default=7, help="+/- days around each date")
    parser.add_argument("--size", type=int, default=256, help="output tile size")
    parser.add_argument("--demo", action="store_true", help="offline synthetic run")
    args = parser.parse_args(argv)

    label, bbox = load_aoi(args.aoi)
    notes_prefix = [f"AOI: {label}"]

    if args.demo:
        rb, nb = synthetic_scene(args.size, seed=1, veg_fraction=0.25)
        ra, na = synthetic_scene(args.size, seed=2, veg_fraction=0.55)
        notes = [*notes_prefix, "demo: synthetic scenes (no network)"]
    else:
        before = (_shift(args.before, -args.window), _shift(args.before, args.window))
        after = (_shift(args.after, -args.window), _shift(args.after, args.window))
        rb, nb, ra, na, fetch_notes = _fetch_real(bbox, before, after, args.size)
        notes = [*notes_prefix, *fetch_notes]

    # Use the AOI slug for filesystem-safe artifact names.
    result = run_pipeline(args.aoi, bbox, rb, nb, ra, na, notes=notes)
    for line in (
        f"AOI: {result.aoi}  bbox={result.bbox}",
        f"NDVI overlay:      {result.ndvi_overlay}",
        f"Change overlay:    {result.change_overlay}",
        f"Detections:        {result.detections_geojson} ({result.detection_count} features)",
        f"Veg coverage:      {result.coverage_fraction:.1%}",
        *[f"  - {n}" for n in result.notes],
    ):
        print(line)
    return 0


def _shift(date: str, days: int) -> str:
    from datetime import date as _date
    from datetime import timedelta

    y, m, d = (int(p) for p in date.split("-"))
    return (_date(y, m, d) + timedelta(days=days)).isoformat()


if __name__ == "__main__":
    sys.exit(main())
