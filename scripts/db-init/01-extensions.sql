-- Runs once on first Postgres init (docker-entrypoint-initdb.d).
-- Enables pgvector so the RAG store (Phase 4) can persist embeddings.
CREATE EXTENSION IF NOT EXISTS vector;
