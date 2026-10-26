"""Local MVP behavior tests. No production security guarantees."""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_incident_routing_and_verified_knowledge():
    created = client.post("/incidents", json={
        "title": "Backup job failed",
        "description": "Nightly database backup reported failure",
        "category": "backup",
        "priority": 1
    })
    assert created.status_code == 201
    item = created.json()
    assert item["assigned_team"] == "Backup Operations"
    incident_id = item["id"]

    no_resolution = client.patch(f"/incidents/{incident_id}", json={
        "status": "resolved", "actor": "demo-engineer"
    })
    assert no_resolution.status_code == 422

    resolved = client.patch(f"/incidents/{incident_id}", json={
        "status": "resolved",
        "actor": "demo-engineer",
        "resolution": "Verified storage connectivity and reran backup successfully."
    })
    assert resolved.status_code == 200

    verified = client.post(
        f"/incidents/{incident_id}/verify-resolution",
        params={"actor": "demo-reviewer"}
    )
    assert verified.status_code == 200
    assert verified.json()["verified_by"] == "demo-reviewer"
    assert client.post(
        f"/incidents/{incident_id}/verify-resolution",
        params={"actor": "demo-reviewer"}
    ).status_code == 409

def test_unknown_category_rejected():
    response = client.post("/incidents", json={
        "title": "Unknown system", "description": "No category mapping",
        "category": "unmapped", "priority": 2
    })
    assert response.status_code == 422

def test_missing_incident_returns_404():
    assert client.patch("/incidents/nonexistent", json={
        "status": "investigating", "actor": "demo"
    }).status_code == 404
