from services.rag.chunk import chunk_markdown, load_kb_chunks
from services.rag.retrieve import retrieve


def test_chunking_splits_on_headings():
    md = "# Title\n\n## A\nalpha body\n\n## B\nbeta body\n"
    chunks = chunk_markdown(md, "doc.md")
    headings = {c.heading for c in chunks}
    assert headings == {"A", "B"}
    assert any("alpha" in c.text for c in chunks)


def test_kb_loads():
    chunks = load_kb_chunks()
    sources = {c.source for c in chunks}
    assert "sentinel-2.md" in sources
    assert len(chunks) >= 5


def test_retrieve_revisit_time():
    out = retrieve("What is Sentinel-2 revisit time?", k=3)
    assert out["chunks"], "expected retrieved chunks"
    assert out["chunks"][0]["source"] == "sentinel-2.md"
    assert out["citations"][0]["source"].startswith("sentinel-2.md#")


def test_retrieve_ndvi_bands():
    out = retrieve("which bands are used to compute NDVI", k=3)
    joined = " ".join(c["text"] for c in out["chunks"])
    assert "B08" in joined or "NIR" in joined


def test_agent_kb_only_answer_has_citations():
    import pytest

    pytest.importorskip("langgraph")
    from langchain_core.messages import HumanMessage, SystemMessage

    from services.agent.graph import build_graph
    from services.agent.models import SYSTEM_PROMPT, ScriptedModel
    from services.agent.service import scripted_answer

    planned = [{"name": "retrieve_knowledge", "args": {"query": "Sentinel-2 revisit time"}}]
    graph = build_graph(ScriptedModel(planned, scripted_answer("central_valley_ca", "", "")))
    final = graph.invoke(
        {
            "messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="revisit?")],
            "artifacts": [],
            "citations": [],
        }
    )

    assert any(c["source"].endswith(".md") or ".md#" in c["source"] for c in final["citations"])
    assert "knowledge base" in final["messages"][-1].content
