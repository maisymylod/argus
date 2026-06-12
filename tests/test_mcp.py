import pytest


def test_mcp_server_registers_tools():
    pytest.importorskip("mcp")
    from services.agent.tools import TOOL_SPECS
    from services.mcp_server.server import build_server

    server = build_server()
    assert server.name == "argus"
    # The server module imports and registers without error for every spec.
    assert len(TOOL_SPECS) == 3


@pytest.mark.integration
def test_mcp_stdio_roundtrip():
    """Spawn the MCP server over stdio and list its tools (offline)."""
    pytest.importorskip("mcp")
    from services.mcp_server.mcp_client import list_tool_names

    names = set(list_tool_names())
    assert {"list_aois", "vegetation_change", "retrieve_knowledge"}.issubset(names)
