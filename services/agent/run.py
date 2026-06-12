"""Run a scripted earth-observation query through the agent (CLI).

Example:
  python -m services.agent --aoi central_valley_ca --before 2023-06-15 --after 2023-09-15

With ANTHROPIC_API_KEY set, Claude plans the tool calls itself. Without a key, a
deterministic scripted plan drives the same graph so the demo runs offline.
"""

from __future__ import annotations

import argparse
import sys

from .service import run_query


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="services.agent")
    parser.add_argument("--aoi", default="central_valley_ca")
    parser.add_argument("--before", default="2023-06-15")
    parser.add_argument("--after", default="2023-09-15")
    parser.add_argument("--query", default=None)
    parser.add_argument("--live", action="store_true", help="use live STAC instead of demo scenes")
    parser.add_argument("--kb-only", action="store_true", help="answer a metadata question via RAG")
    args = parser.parse_args(argv)

    result = run_query(
        aoi=args.aoi,
        before=args.before,
        after=args.after,
        query=args.query,
        kb_only=args.kb_only,
        live=args.live,
    )

    print(f"== Argus agent ({result['mode']}) ==")
    print(f"Q: {result['query']}\n")
    print(f"A: {result['answer']}\n")
    if result["artifacts"]:
        print("Artifacts:")
        for art in result["artifacts"]:
            print(f"  - [{art['kind']}/{art.get('role', '')}] {art['url']}")
    print("Citations:")
    for cite in result["citations"]:
        print(f"  - {cite['source']}: {cite['detail']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
