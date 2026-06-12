"""Canonical geospatial tool definitions.

These specs are the single source of truth: the agent binds them to the model
for tool-calling, and the MCP server (services/mcp_server) exposes the same
functions over the Model Context Protocol. Each function returns a JSON-
serializable dict that includes any artifacts and citations it produced.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass

from pydantic import BaseModel, Field

from services.imagery.aois import AOIS_DIR, load_aoi
from services.imagery.pipeline import run_pipeline, synthetic_scene


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    args_model: type[BaseModel]
    fn: Callable[..., dict]


# --- list_aois -------------------------------------------------------------


class ListAOIsArgs(BaseModel):
    pass


def list_aois() -> dict:
    """List the available areas of interest and their bounding boxes."""
    aois = []
    for path in sorted(AOIS_DIR.glob("*.geojson")):
        label, bbox = load_aoi(path.stem)
        aois.append({"name": path.stem, "label": label, "bbox": bbox})
    return {"aois": aois}


# --- vegetation_change -----------------------------------------------------


class VegetationChangeArgs(BaseModel):
    aoi: str = Field(description="AOI name from list_aois, e.g. central_valley_ca")
    before: str = Field(description="before date YYYY-MM-DD")
    after: str = Field(description="after date YYYY-MM-DD")
    demo: bool = Field(default=True, description="offline synthetic scenes; false for live STAC")


def _fetch_pair(bbox: list[float], date: str, window: int, size: int):
    from datetime import date as _date
    from datetime import timedelta

    from services.imagery.stac import open_catalog, read_red_nir, search_least_cloudy

    y, m, d = (int(p) for p in date.split("-"))
    center = _date(y, m, d)
    lo = (center - timedelta(days=window)).isoformat()
    hi = (center + timedelta(days=window)).isoformat()
    stac_url = os.environ.get("STAC_URL", "https://planetarycomputer.microsoft.com/api/stac/v1")
    catalog = open_catalog(stac_url)
    item = search_least_cloudy(catalog, bbox, (lo, hi))
    if item is None:
        raise ValueError(f"No cloud-free scene near {date}")
    red, nir = read_red_nir(item, bbox, size)
    cite = {
        "source": item.id,
        "detail": f"sentinel-2-l2a, cloud {item.properties.get('eo:cloud_cover', '?')}%",
    }
    return red, nir, cite


def vegetation_change(aoi: str, before: str, after: str, demo: bool = True) -> dict:
    """Compute NDVI vegetation change for an AOI between two dates.

    Returns summary stats, rendered overlay paths, a GeoJSON detection layer,
    and citations to the source scenes.
    """
    label, bbox = load_aoi(aoi)
    if demo:
        red_b, nir_b = synthetic_scene(seed=1, veg_fraction=0.25)
        red_a, nir_a = synthetic_scene(seed=2, veg_fraction=0.55)
        notes = [f"AOI: {label}", "demo synthetic scenes (offline)"]
        citations = [{"source": "sentinel-2-l2a (demo)", "detail": "synthetic scenes, no network"}]
    else:
        red_b, nir_b, cite_b = _fetch_pair(bbox, before, 7, 256)
        red_a, nir_a, cite_a = _fetch_pair(bbox, after, 7, 256)
        notes = [f"AOI: {label}", "live Sentinel-2 L2A"]
        citations = [cite_b, cite_a]

    result = run_pipeline(aoi, bbox, red_b, nir_b, red_a, nir_a, notes=notes)
    return {
        "aoi": label,
        "bbox": bbox,
        "window": {"before": before, "after": after},
        "stats": {
            "coverage_fraction": result.coverage_fraction,
            "detection_count": result.detection_count,
        },
        "summary": (
            f"{result.detection_count} vegetation features detected, "
            f"{result.coverage_fraction:.1%} of the AOI vegetated in the later scene"
        ),
        "artifacts": [
            {"kind": "raster_overlay", "role": "ndvi", "uri": str(result.ndvi_overlay)},
            {"kind": "raster_overlay", "role": "change", "uri": str(result.change_overlay)},
            {"kind": "geojson", "role": "detections", "uri": str(result.detections_geojson)},
        ],
        "citations": citations,
    }


# --- retrieve_knowledge (RAG lands in Phase 4) -----------------------------


class RetrieveKnowledgeArgs(BaseModel):
    query: str = Field(description="natural-language question about sensors, bands, or places")
    k: int = Field(default=4, description="number of chunks to retrieve")


def retrieve_knowledge(query: str, k: int = 4) -> dict:
    """Retrieve grounding passages from the geospatial knowledge base.

    Phase 3 returns an empty result; Phase 4 wires this to pgvector retrieval.
    """
    return {"query": query, "chunks": [], "citations": [], "note": "RAG retrieval lands in Phase 4"}


def _spec(name: str, args_model: type[BaseModel], fn: Callable[..., dict]) -> ToolSpec:
    return ToolSpec(name, fn.__doc__ or "", args_model, fn)


TOOL_SPECS: list[ToolSpec] = [
    _spec("list_aois", ListAOIsArgs, list_aois),
    _spec("vegetation_change", VegetationChangeArgs, vegetation_change),
    _spec("retrieve_knowledge", RetrieveKnowledgeArgs, retrieve_knowledge),
]

_SPECS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}


def get_spec(name: str) -> ToolSpec:
    return _SPECS_BY_NAME[name]


def as_langchain_tools() -> list:
    """Expose the specs as LangChain StructuredTools for model.bind_tools()."""
    from langchain_core.tools import StructuredTool

    return [
        StructuredTool.from_function(
            func=spec.fn,
            name=spec.name,
            description=spec.description,
            args_schema=spec.args_model,
        )
        for spec in TOOL_SPECS
    ]
