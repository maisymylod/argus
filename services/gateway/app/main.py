import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.imagery.pipeline import OUT_DIR

from .config import settings

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title="Argus Gateway",
    version="0.2.0",
    summary="Public boundary for the Argus earth-observation agent and services.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    aoi: str = "central_valley_ca"
    before: str = "2023-06-15"
    after: str = "2023-09-15"
    query: str | None = None
    kb_only: bool = False
    live: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker Compose and Kubernetes."""
    return {"status": "ok", "service": "gateway", "version": app.version}


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "argus-gateway", "docs": "/docs", "health": "/health"}


@app.post("/agent/query")
def agent_query(req: QueryRequest) -> dict:
    """Run a natural-language earth-observation query through the agent."""
    # Imported lazily so /health stays cheap and import errors surface per-request.
    from services.agent.service import run_query

    return run_query(
        aoi=req.aoi,
        before=req.before,
        after=req.after,
        query=req.query,
        kb_only=req.kb_only,
        live=req.live,
    )


@app.get("/artifacts/{name}")
def artifact(name: str) -> FileResponse:
    """Serve a generated overlay PNG or GeoJSON detection layer."""
    if "/" in name or ".." in name:
        raise HTTPException(status_code=400, detail="invalid artifact name")
    path = OUT_DIR / name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="artifact not found")
    return FileResponse(path)
