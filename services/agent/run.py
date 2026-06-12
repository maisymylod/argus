"""Run a scripted earth-observation query through the agent.

Example:
  python -m services.agent --aoi central_valley_ca --before 2023-06-15 --after 2023-09-15

With ANTHROPIC_API_KEY set, Claude plans the tool calls itself. Without a key, a
deterministic scripted plan drives the same graph so the demo runs offline.
"""

from __future__ import annotations

import argparse
import os
import sys

from langchain_core.messages import HumanMessage, SystemMessage

from .graph import build_graph
from .models import SYSTEM_PROMPT, get_model


def _scripted_answer(aoi: str, before: str, after: str):
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="services.agent")
    parser.add_argument("--aoi", default="central_valley_ca")
    parser.add_argument("--before", default="2023-06-15")
    parser.add_argument("--after", default="2023-09-15")
    parser.add_argument("--query", default=None)
    parser.add_argument("--live", action="store_true", help="use live STAC instead of demo scenes")
    parser.add_argument("--kb-only", action="store_true", help="answer a metadata question via RAG")
    args = parser.parse_args(argv)

    if args.kb_only:
        query = args.query or "What is Sentinel-2's revisit time and which bands compute NDVI?"
        planned = [{"name": "retrieve_knowledge", "args": {"query": query}}]
    else:
        query = args.query or (
            f"Show vegetation change near {args.aoi} between {args.before} and {args.after}, "
            f"and note the sensor's revisit time."
        )
        planned = [
            {
                "name": "vegetation_change",
                "args": {
                    "aoi": args.aoi,
                    "before": args.before,
                    "after": args.after,
                    "demo": not args.live,
                },
            },
            {"name": "retrieve_knowledge", "args": {"query": query}},
        ]

    model = get_model(planned, _scripted_answer(args.aoi, args.before, args.after))
    graph = build_graph(model)

    initial = {
        "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=query)],
        "artifacts": [],
        "citations": [],
    }
    final = graph.invoke(initial)

    mode = "live Claude" if os.environ.get("ANTHROPIC_API_KEY") else "scripted (offline)"
    print(f"== Argus agent ({mode}) ==")
    print(f"Q: {query}\n")
    print(f"A: {final['messages'][-1].content}\n")
    print("Artifacts:")
    for art in final["artifacts"]:
        print(f"  - [{art['kind']}/{art.get('role', '')}] {art['uri']}")
    print("Citations:")
    for cite in final["citations"]:
        print(f"  - {cite['source']}: {cite['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
