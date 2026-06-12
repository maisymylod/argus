"""Synchronous helper to exercise the MCP server over stdio.

Spawns `python -m services.mcp_server`, lists the exposed tools, and optionally
calls one. Used by the integration test and as a reference for wiring the agent
to consume tools over MCP (set ARGUS_USE_MCP=1).
"""

from __future__ import annotations

import asyncio
import sys


async def _list_tools_async() -> list[str]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable, args=["-m", "services.mcp_server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            return [t.name for t in tools.tools]


def list_tool_names() -> list[str]:
    """Return the tool names advertised by the running MCP server."""
    return asyncio.run(_list_tools_async())


if __name__ == "__main__":
    print(list_tool_names())
