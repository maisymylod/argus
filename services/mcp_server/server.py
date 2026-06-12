"""FastMCP server that exposes the canonical Argus tools over MCP.

Run as a stdio server (the transport MCP hosts such as Claude Desktop use):
  python -m services.mcp_server

The tools are the exact same functions the agent calls (services.agent.tools),
so there is one definition exposed two ways.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from services.agent.tools import TOOL_SPECS


def build_server() -> FastMCP:
    server = FastMCP("argus")
    for spec in TOOL_SPECS:
        server.add_tool(spec.fn, name=spec.name, description=spec.description)
    return server


mcp = build_server()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
