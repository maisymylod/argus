"""Shared domain models used across services.

Defined in Phase 1 as the common vocabulary; consumed by the imagery, ML,
agent, and RAG services in later phases.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start: str = Field(description="ISO date, inclusive, e.g. 2023-06-01")
    end: str = Field(description="ISO date, inclusive, e.g. 2023-06-30")


class AOI(BaseModel):
    """Area of interest as a GeoJSON-style bounding box [west, south, east, north]."""

    name: str
    bbox: tuple[float, float, float, float]


class Citation(BaseModel):
    source: str = Field(description="KB document id or STAC item id")
    detail: str = Field(default="", description="Snippet, band, or scene reference")


class Artifact(BaseModel):
    """A structured result the agent hands back to the frontend to render."""

    kind: str = Field(description="geojson | raster_overlay | layer")
    uri: str = Field(description="Path or URL the frontend can load")
    citations: list[Citation] = Field(default_factory=list)
