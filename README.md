# Argus

Natural-language exploration of public earth-observation imagery, powered by an
LLM agent that calls geospatial tools over the Model Context Protocol (MCP),
grounds its answers with retrieval (RAG), and renders results on an interactive
WebGL map. One coherent system that exercises full-stack AI interaction,
tool-calling orchestration, MCP, vector search, image and ML processing, and
container orchestration across local and cluster environments.

![Argus demo](docs/demo.gif)

> The GIF above is a placeholder until recorded. See `docs/DEMO.md`.

## Data policy

Argus uses public, open earth-observation data only. Primary source is
Sentinel-2 L2A via the Microsoft Planetary Computer public STAC API, with AWS
Open Data and NASA GIBS tiles as alternatives. No proprietary, classified, or
ITAR-controlled data is used, fetched, or stored, ever. The knowledge base under
`data/kb/` is limited to open documentation about public sensors, bands, revisit
times, and place metadata.

## Architecture

```
Browser  (React + TypeScript + Redux Toolkit + deck.gl)
   |  chat drives the agent; results animate onto the map
   v
FastAPI gateway  (POST /agent/query, GET /artifacts/{name})
   |
   v
LangGraph agent  (Claude or scripted)  plan -> act -> synthesize
   |  RAG retrieve (pgvector or in-memory)
   |  tool calls over the shared tool layer (also served via MCP)
   v
tools:  imagery (STAC, rasterio, NDVI, change)
        ml      (onnxruntime -> GeoJSON detections)
        rag     (knowledge-base retrieval)
Postgres + pgvector:  embeddings, metadata
MCP server (services/mcp_server):  the same tools over Model Context Protocol
```

The geospatial tools are defined once (`services/agent/tools.py`) and exposed two
ways: bound to the model for tool-calling, and served over MCP by a FastMCP stdio
server that any MCP host (for example Claude Desktop) can connect to.

## JD skill to file map

| Skill | Where it lives |
| --- | --- |
| React / Redux, graphics-intensive web | `web/` (Redux Toolkit store, RTK Query, deck.gl `MapView`) |
| Python applications | `services/` |
| Web services and distributed applications | `services/gateway/`, `docker-compose.yml`, `deploy/` |
| RAG pipelines | `services/rag/` (chunk, embed, store, retrieve) |
| Tool callers / AI orchestration | `services/agent/graph.py`, `services/agent/tools.py` |
| Model Context Protocol | `services/mcp_server/` |
| Vector / high-performance databases | Postgres + pgvector (`services/rag/store.py`, `services/rag/schema.sql`) |
| Image data processing | `services/imagery/` (rasterio, STAC, NDVI, change) |
| Machine learning | `services/ml/` (onnxruntime + model card) |
| Kubernetes / container orchestration | `deploy/helm/`, `deploy/k8s/`, `scripts/kind-*.sh`, Dockerfiles |
| Linux, SSH, scripting | `scripts/`, `Makefile` |
| Secrets discipline | `.env.example`, `scripts/secret-scan.sh`, `.pre-commit-config.yaml` |

## Run it

### Docker Compose (laptop)

Prerequisites: Docker with Compose v2.

```bash
make up        # build and start db (pgvector), gateway API, web
```

- Web: http://localhost:8080
- Gateway health: http://localhost:8000/health
- Gateway API docs: http://localhost:8000/docs

```bash
make down      # stop the stack
make seed      # ingest the knowledge base into pgvector (optional; RAG works in-memory by default)
```

### Kubernetes on kind (cloud-portable, from the same images)

Prerequisites: Docker, kind, kubectl, Helm.

```bash
make k8s-up    # create kind cluster, build + load images, helm install
# open http://localhost:8080
make k8s-down  # delete the cluster
```

The same images run under Docker Compose and on kind, demonstrating portability
across local and cluster networks.

### CLI demos (no browser)

```bash
make agent-demo   # scripted vegetation-change query (offline)
make kb-demo      # sensor-metadata question answered from the knowledge base (RAG)
make mcp-tools    # list the tools exposed over MCP
python -m services.imagery --aoi central_valley_ca --before 2023-06-15 --after 2023-09-15 --demo
```

With `ANTHROPIC_API_KEY` set, the agent uses Claude to plan tool calls; without
a key it falls back to a deterministic scripted plan so everything runs offline.
Add `--live` (CLI) to fetch real Sentinel-2 scenes instead of synthetic demo
imagery.

## Development

```bash
make lint        # ruff check + format check
make test        # pytest (integration tests, which need network or a DB, are skipped)
make typecheck   # mypy
cd web && npm install && npm run build   # type-check and bundle the frontend
```

CI (`.github/workflows/ci.yml`) runs lint, tests, the secret scan, and builds
the web image on every push and PR.

## Secrets

No secrets are committed. All keys are supplied via environment variables. Copy
`.env.example` to `.env` (gitignored) and fill in values such as
`ANTHROPIC_API_KEY`. A pre-commit secret scan (gitleaks) and a deterministic CI
backstop (`scripts/secret-scan.sh`) guard against accidental commits. Install
hooks with `bash scripts/setup.sh`.

## Models and ML

- LLM: Claude via the Anthropic API (`claude-sonnet-4-6` by default).
- Vision model: a compact ONNX vegetation segmenter built reproducibly by
  `services/ml/build_model.py` (no training, no download). See
  `services/ml/model_card.md` for what it is and how to swap in a real
  pretrained model.

## License

Public-data portfolio project. See `data/` for sources and attribution.
