from fastapi.testclient import TestClient
from app.main import app, incidents

client = TestClient(app)

def setup_function():
    incidents.clear()

def test_health():
    assert client.get("/health").json()["status"] == "ok"

def test_incident_lifecycle():
    created = client.post("/api/v1/incidents", json={"title": "VPN outage", "severity": "critical"})
    assert created.status_code == 201
    incident_id = created.json()["id"]
    assert client.get("/api/v1/dashboard").json()["critical_incidents"] == 1
    assert client.patch(f"/api/v1/incidents/{incident_id}/resolve").json()["status"] == "resolved"
    assert client.get("/api/v1/dashboard").json()["open_incidents"] == 0

def test_invalid_severity():
    assert client.post("/api/v1/incidents", json={"title": "Test", "severity": "extreme"}).status_code == 422
