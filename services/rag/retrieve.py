"""Retrieval entry point used by the agent's retrieve_knowledge tool.

Defaults to an in-memory index built from data/kb (no external dependencies).
Set ARGUS_RAG_BACKEND=pgvector to query the Postgres + pgvector store instead.
"""

from __future__ import annotations

import os

from .chunk import load_kb_chunks
from .embeddings import embed_one, embed_texts
from .store import InMemoryVectorStore, PgVectorStore

_MEMORY_INDEX: InMemoryVectorStore | None = None


def build_memory_index() -> InMemoryVectorStore:
    """Embed every KB chunk into a fresh in-memory store."""
    chunks = load_kb_chunks()
    store = InMemoryVectorStore()
    if chunks:
        vectors = embed_texts([c.text for c in chunks])
        metas = [{"source": c.source, "heading": c.heading, "text": c.text} for c in chunks]
        store.add(vectors, metas)
    return store


def _default_store():
    if os.environ.get("ARGUS_RAG_BACKEND") == "pgvector":
        return PgVectorStore.from_env()
    global _MEMORY_INDEX
    if _MEMORY_INDEX is None:
        _MEMORY_INDEX = build_memory_index()
    return _MEMORY_INDEX


def _snippet(text: str, limit: int = 160) -> str:
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def retrieve(query: str, k: int = 4) -> dict:
    """Return the top-k KB chunks for a query, with citations."""
    store = _default_store()
    hits = store.search(embed_one(query), k)
    chunks = [
        {
            "source": h["source"],
            "heading": h["heading"],
            "text": h["text"],
            "score": round(h.get("score", 0.0), 4),
        }
        for h in hits
    ]
    citations = [
        {"source": f"{h['source']}#{h['heading']}", "detail": _snippet(h["text"])} for h in hits
    ]
    return {"query": query, "chunks": chunks, "citations": citations}
