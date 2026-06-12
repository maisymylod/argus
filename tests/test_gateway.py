import pytest
from fastapi.testclient import TestClient

from services.gateway.app.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "gateway"


def test_root_links():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["health"] == "/health"


def test_artifact_rejects_traversal():
    resp = client.get("/artifacts/..%2f..%2fetc%2fpasswd")
    assert resp.status_code in (400, 404)


def test_agent_query_and_artifact_roundtrip():
    pytest.importorskip("langgraph")
    pytest.importorskip("onnxruntime")

    resp = client.post(
        "/agent/query",
        json={"aoi": "central_valley_ca", "before": "2023-06-15", "after": "2023-09-15"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["answer"]
    assert body["bbox"] and len(body["bbox"]) == 4
    urls = [a["url"] for a in body["artifacts"]]
    assert any(u.endswith(".geojson") for u in urls)

    # The served artifact URL should resolve through the gateway.
    art = client.get(urls[0])
    assert art.status_code == 200
