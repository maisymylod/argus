"""Vector stores: an in-memory cosine index and a pgvector-backed store.

Both expose the same minimal interface:
  - add(vectors: np.ndarray, metas: list[dict]) -> None
  - search(query: np.ndarray, k: int) -> list[dict]  # metas with a 'score'
"""

from __future__ import annotations

import os

import numpy as np


class InMemoryVectorStore:
    """Cosine-similarity search over unit vectors held in memory."""

    def __init__(self) -> None:
        self._vectors: np.ndarray | None = None
        self._metas: list[dict] = []

    def add(self, vectors: np.ndarray, metas: list[dict]) -> None:
        self._vectors = vectors if self._vectors is None else np.vstack([self._vectors, vectors])
        self._metas.extend(metas)

    def search(self, query: np.ndarray, k: int = 4) -> list[dict]:
        if self._vectors is None or not self._metas:
            return []
        scores = self._vectors @ query  # unit vectors => cosine similarity
        top = np.argsort(scores)[::-1][:k]
        return [{**self._metas[i], "score": float(scores[i])} for i in top]


class PgVectorStore:
    """Postgres + pgvector store. Lazy-imports psycopg so offline runs do not need it."""

    def __init__(self, dsn: str, table: str = "kb_chunks") -> None:
        self._dsn = dsn
        self._table = table

    @classmethod
    def from_env(cls) -> PgVectorStore:
        dsn = os.environ.get("DATABASE_URL")
        if not dsn:
            raise RuntimeError("DATABASE_URL is required for the pgvector store")
        return cls(dsn)

    def _connect(self):
        import psycopg
        from pgvector.psycopg import register_vector

        conn = psycopg.connect(self._dsn)
        register_vector(conn)
        return conn

    def add(self, vectors: np.ndarray, metas: list[dict]) -> None:
        with self._connect() as conn, conn.cursor() as cur:
            for vec, meta in zip(vectors, metas, strict=True):
                cur.execute(
                    f"INSERT INTO {self._table} (source, heading, text, embedding) "
                    "VALUES (%s, %s, %s, %s)",
                    (meta["source"], meta["heading"], meta["text"], np.asarray(vec)),
                )
            conn.commit()

    def search(self, query: np.ndarray, k: int = 4) -> list[dict]:
        with self._connect() as conn, conn.cursor() as cur:
            cur.execute(
                f"SELECT source, heading, text, 1 - (embedding <=> %s) AS score "
                f"FROM {self._table} ORDER BY embedding <=> %s LIMIT %s",
                (np.asarray(query), np.asarray(query), k),
            )
            rows = cur.fetchall()
        return [{"source": r[0], "heading": r[1], "text": r[2], "score": float(r[3])} for r in rows]
