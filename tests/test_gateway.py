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
