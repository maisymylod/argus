-- Knowledge-base chunk store for RAG retrieval.
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS kb_chunks (
    id        SERIAL PRIMARY KEY,
    source    TEXT NOT NULL,
    heading   TEXT NOT NULL,
    text      TEXT NOT NULL,
    embedding vector(256)
);

-- Cosine-distance index (effective once enough rows are present).
CREATE INDEX IF NOT EXISTS kb_chunks_embedding_idx
    ON kb_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
