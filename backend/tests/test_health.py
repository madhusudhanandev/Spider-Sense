"""
Minimal smoke test. Run with `pytest` from backend/.

Note: requires DATABASE_URL to point at a reachable Postgres instance for
the app's startup event (create_all) to succeed; the health check itself
does not touch the database.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "Spider-Sense AI"
