import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

logging.basicConfig(level=settings.log_level)

app = FastAPI(
    title="Argus Gateway",
    version="0.1.0",
    summary="Public boundary for the Argus earth-observation agent and services.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker Compose and (later) Kubernetes."""
    return {"status": "ok", "service": "gateway", "version": app.version}


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "argus-gateway", "docs": "/docs", "health": "/health"}
