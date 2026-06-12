"""Programmatic entry point for running an agent query (used by the gateway API).

Returns a JSON-serializable dict: answer, the AOI bbox, artifact URLs the API
can serve, and citations. The CLI (run.py) is a thin wrapper over this.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from .graph import build_graph
from .models import SYSTEM_PROMPT, get_model

DEFAULT_KB_QUESTION = "What is Sentinel-2's revisit time and which bands compute NDVI?"


def scripted_answer(aoi: str, before: str, after: str):
    def answer(results: list[dict]) -> str:
        veg = next((r for r in results if "stats" in r), {})
        kb = next((r for r in results if "chunks" in r), {})
        cites = [c for r in results for c in r.get("citations", [])]
        cite_str = "; ".join(f"{c['source']} ({c['detail']})" for c in cites) or "none"

        parts = []
        if veg:
            parts.append(
                f"Between {before} and {after}, {veg['summary']} for {veg.get('aoi', aoi)}. "
                "Rendered NDVI and change overlays plus a GeoJSON detection layer are attached."
            )
        top_chunk = (kb.get("chunks") or [{}])[0]
        if top_chunk.get("text"):
            parts.append(
                f"From the knowledge base ({top_chunk['source']} / {top_chunk['heading']}): "
                f"{' '.join(top_chunk['text'].split())[:200]}"
            )
        parts.append(f"Sources: {cite_str}.")
        return " ".join(parts)

    return answer


def _planned_calls(aoi, before, after, query, kb_only, live):
    if kb_only:
        return [{"name": "retrieve_knowledge", "args": {"query": query}}]
    return [
        {
            "name": "vegetation_change",
            "args": {"aoi": aoi, "before": before, "after": after, "demo": not live},
        },
        {"name": "retrieve_knowledge", "args": {"query": query}},
    ]


def run_query(
    aoi: str = "central_valley_ca",
    before: str = "2023-06-15",
    after: str = "2023-09-15",
    query: str | None = None,
    kb_only: bool = False,
    live: bool = False,
) -> dict:
    """Run one query through the agent graph and return a serializable result."""
    if kb_only:
        query = query or DEFAULT_KB_QUESTION
    else:
        query = query or (
            f"Show vegetation change near {aoi} between {before} and {after}, "
            "and note the sensor's revisit time."
        )

    planned = _planned_calls(aoi, before, after, query, kb_only, live)
    model = get_model(planned, scripted_answer(aoi, before, after))
    graph = build_graph(model)

    final = graph.invoke(
        {
            "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)],
            "artifacts": [],
            "citations": [],
        }
    )

    bbox, aoi_label = None, aoi
    for msg in final["messages"]:
        if isinstance(msg, ToolMessage) and msg.name == "vegetation_change":
            data = json.loads(msg.content)
            bbox = data.get("bbox")
            aoi_label = data.get("aoi", aoi)

    artifacts = [
        {"kind": a["kind"], "role": a.get("role"), "url": f"/artifacts/{Path(a['uri']).name}"}
        for a in final["artifacts"]
    ]

    return {
        "mode": "live-claude" if os.environ.get("ANTHROPIC_API_KEY") else "scripted",
        "query": query,
        "answer": final["messages"][-1].content,
        "aoi": aoi_label,
        "bbox": bbox,
        "artifacts": artifacts,
        "citations": final["citations"],
    }
