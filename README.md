# Argus

Natural-language exploration of public earth-observation imagery, powered by an
LLM agent that calls geospatial tools over the Model Context Protocol (MCP),
grounds its answers with retrieval (RAG), and renders results on an interactive
map. Built as a single coherent system that exercises full-stack AI interaction,
tool-calling orchestration, MCP, vector search, image and ML processing, and
container orchestration across local and cluster environments.

> Status: Phase 1 (skeleton and infrastructure). The full phase plan is below.

## Data policy

Argus uses public, open earth-observation data only. Primary source is
Sentinel-2 L2A via the Microsoft Planetary Computer public STAC API, with AWS
Open Data and NASA GIBS tiles as alternatives. No proprietary, classified, or
ITAR-controlled data is used, fetched, or stored, ever. The knowledge base
under `data/kb/` is limited to open documentation about public sensors, bands,
revisit times, and place metadata.

## Architecture

```
Browser (React + Redux + MapLibre/deck.gl)
   |  chat + map layers
   v
FastAPI gateway  -->  LangGraph agent (Claude)
                         |  RAG retrieve (pgvector)
                         |  tool calls over MCP
                         v
                      MCP server  -->  imagery (STAC, rasterio, NDVI, change)
                                  -->  ml (onnxruntime -> GeoJSON)
                                  -->  rag (pgvector retrieval)
Postgres + pgvector: embeddings, metadata, tile cache
```

## JD skill to file map

| Skill | Where it lives |
| --- | --- |
| React / Redux, graphics-intensive web | `web/` (stub in Phase 1, full app in Phase 5) |
| Python applications | `services/` |
| Web services and distributed applications | `services/gateway/`, `docker-compose.yml`, `deploy/` |
| RAG pipelines | `services/rag/` (Phase 4) |
| Tool callers / AI orchestration | `services/agent/` (Phase 3) |
| Model Context Protocol | `services/mcp_server/` (Phase 3) |
| Vector / high-performance databases | Postgres + pgvector (`scripts/db-init/`, compose `db`) |
| Image data processing | `services/imagery/` (Phase 2) |
| Machine learning | `services/ml/` (Phase 2) |
| Kubernetes / container orchestration | `deploy/`, `scripts/kind-*.sh`, Dockerfiles (Phase 6) |
| Linux, SSH, scripting | `scripts/`, `Makefile` |
| Secrets discipline | `.env.example`, `scripts/secret-scan.sh`, `.pre-commit-config.yaml` |

## Quickstart

Prerequisites: Docker with Compose v2.

```bash
make up      # build and start db (pgvector), gateway, web stub
```

Then open:

- Web stub: http://localhost:8080
- Gateway health: http://localhost:8000/health
- Gateway API docs: http://localhost:8000/docs

```bash
make down    # stop the stack
make logs    # tail logs
make test    # run python tests
make lint    # ruff check + format check
```

## Secrets

No secrets are committed. All keys are supplied via environment variables.
Copy `.env.example` to `.env` (gitignored) and fill in values such as
`ANTHROPIC_API_KEY` when the agent phase needs it. A pre-commit secret scan
(gitleaks) and a deterministic CI backstop (`scripts/secret-scan.sh`) guard
against accidental commits. Install hooks with `bash scripts/setup.sh`.

## Build phases

- Phase 0: Plan. Done.
- Phase 1: Skeleton and infra (compose, gateway, web stub, Makefile, CI, README). This commit.
- Phase 2: Imagery and ML service (STAC fetch, NDVI, change detection, ONNX to GeoJSON).
- Phase 3: MCP server and LangGraph agent (tool calls over MCP, cited answers).
- Phase 4: RAG ingest into pgvector wired into the agent.
- Phase 5: React + Redux + MapLibre/deck.gl frontend, end-to-end browser demo.
- Phase 6: Kubernetes on kind (Helm), finalized README and demo.

## License

Public-data portfolio project. See `data/` for sources and attribution.
