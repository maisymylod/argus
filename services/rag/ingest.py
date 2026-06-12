"""Ingest the knowledge base into Postgres + pgvector.

python -m services.rag.ingest            # uses DATABASE_URL
python -m services.rag.ingest --reset    # drop and recreate rows first
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .chunk import load_kb_chunks
from .embeddings import embed_texts

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def _apply_schema(conn, reset: bool) -> None:
    with conn.cursor() as cur:
        cur.execute(SCHEMA_PATH.read_text())
        if reset:
            cur.execute("TRUNCATE kb_chunks RESTART IDENTITY")
    conn.commit()


def ingest(dsn: str, reset: bool = False) -> int:
    import psycopg
    from pgvector.psycopg import register_vector

    chunks = load_kb_chunks()
    vectors = embed_texts([c.text for c in chunks])

    conn = psycopg.connect(dsn)
    register_vector(conn)
    try:
        _apply_schema(conn, reset)
        with conn.cursor() as cur:
            for chunk, vec in zip(chunks, vectors, strict=True):
                cur.execute(
                    "INSERT INTO kb_chunks (source, heading, text, embedding) "
                    "VALUES (%s, %s, %s, %s)",
                    (chunk.source, chunk.heading, chunk.text, vec),
                )
        conn.commit()
    finally:
        conn.close()
    return len(chunks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="services.rag.ingest")
    parser.add_argument("--reset", action="store_true", help="truncate existing rows first")
    args = parser.parse_args(argv)

    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        print("DATABASE_URL is not set", file=sys.stderr)
        return 1

    count = ingest(dsn, reset=args.reset)
    print(f"ingested {count} knowledge-base chunks into pgvector")
    return 0


if __name__ == "__main__":
    sys.exit(main())
