import pytest

from services.agent.tools import TOOL_SPECS, get_spec, list_aois


def test_tool_registry_names():
    names = {s.name for s in TOOL_SPECS}
    assert names == {"list_aois", "vegetation_change", "retrieve_knowledge"}


def test_list_aois_returns_known_aoi():
    out = list_aois()
    names = {a["name"] for a in out["aois"]}
    assert "central_valley_ca" in names
    for a in out["aois"]:
        assert len(a["bbox"]) == 4


def test_retrieve_knowledge_is_wired_to_rag():
    out = get_spec("retrieve_knowledge").fn(query="Sentinel-2 revisit time", k=2)
    assert out["chunks"], "retrieve_knowledge should return KB chunks in Phase 4"
    assert out["citations"][0]["source"].endswith(".md") or "#" in out["citations"][0]["source"]


def test_scripted_agent_end_to_end():
    pytest.importorskip("langgraph")
    pytest.importorskip("onnxruntime")
    pytest.importorskip("rasterio")

    from langchain_core.messages import HumanMessage, SystemMessage

    from services.agent.graph import build_graph
    from services.agent.models import SYSTEM_PROMPT, ScriptedModel

    planned = [
        {
            "name": "vegetation_change",
            "args": {
                "aoi": "central_valley_ca",
                "before": "2023-06-15",
                "after": "2023-09-15",
                "demo": True,
            },
        },
    ]

    def answer(results):
        veg = next(r for r in results if "summary" in r)
        return f"Result: {veg['summary']}"

    graph = build_graph(ScriptedModel(planned, answer))
    final = graph.invoke(
        {
            "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="veg change?")],
            "artifacts": [],
            "citations": [],
        }
    )

    answer_text = final["messages"][-1].content
    assert "Result:" in answer_text
    # The tool produced structured artifacts and at least one citation.
    kinds = {a["kind"] for a in final["artifacts"]}
    assert {"raster_overlay", "geojson"}.issubset(kinds)
    assert len(final["citations"]) >= 1
