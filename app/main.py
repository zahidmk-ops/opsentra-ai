"""OPSENTRA AI: local-only MVP API. Not suitable for production deployment."""
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="OPSENTRA AI", version="0.1.0", description="Enterprise IT Intelligence & Automation | Powered by PGU Systems")
_lock = RLock()
_incidents: dict[str, dict] = {}
_audit: list[dict] = []
_knowledge: list[dict] = []

# Demo routing only. Production routing must be customer-configurable.
ROUTING = {
    "network": "Network Operations",
    "server": "Systems Administration",
    "backup": "Backup Operations",
    "security": "Security Operations",
    "erp": "ERP Support",
    "endpoint": "IT Service Desk",
}


class Status(str, Enum):
    open = "open"
    investigating = "investigating"
    resolved = "resolved"
    closed = "closed"


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=3000)
    category: str
    priority: int = Field(ge=1, le=4)


class IncidentUpdate(BaseModel):
    status: Status
    actor: str = Field(min_length=1, max_length=120)
    resolution: str | None = None


def record(incident_id: str, action: str, actor: str) -> None:
    _audit.append({"incident_id": incident_id, "action": action, "actor": actor, "at": datetime.now(timezone.utc).isoformat()})


@app.get("/health")
def health():
    return {"status": "ok", "service": "opsentra-ai"}


@app.post("/incidents", status_code=201)
def create_incident(payload: IncidentCreate):
    category = payload.category.strip().lower()
    if category not in ROUTING:
        raise HTTPException(422, f"Unknown category. Allowed: {', '.join(ROUTING)}")
    with _lock:
        incident_id = str(uuid4())
        incident = {
            "id": incident_id,
            "title": payload.title,
            "description": payload.description,
            "category": category,
            "priority": payload.priority,
            "assigned_team": ROUTING[category],
            "status": Status.open.value,
            "resolution": None,
        }
        _incidents[incident_id] = incident
        record(incident_id, "created_and_routed", "system")
        return incident.copy()


@app.get("/incidents")
def list_incidents():
    with _lock:
        return [incident.copy() for incident in _incidents.values()]


@app.patch("/incidents/{incident_id}")
def update_incident(incident_id: str, payload: IncidentUpdate):
    with _lock:
        incident = _incidents.get(incident_id)
        if incident is None:
            raise HTTPException(404, "Incident not found")
        if payload.status in (Status.resolved, Status.closed) and not (payload.resolution or incident["resolution"]):
            raise HTTPException(422, "Resolution documentation is required")
        incident["status"] = payload.status.value
        if payload.resolution:
            incident["resolution"] = payload.resolution
        record(incident_id, f"status_changed_to_{payload.status.value}", payload.actor)
        return incident.copy()


@app.post("/incidents/{incident_id}/verify-resolution")
def verify_resolution(incident_id: str, actor: str):
    """Human attestation; no AI-generated resolution is trusted automatically."""
    with _lock:
        incident = _incidents.get(incident_id)
        if incident is None:
            raise HTTPException(404, "Incident not found")
        if incident["status"] not in ("resolved", "closed") or not incident["resolution"]:
            raise HTTPException(409, "Incident must be resolved with documentation first")
        if any(item["incident_id"] == incident_id for item in _knowledge):
            raise HTTPException(409, "Resolution already verified")
        entry = {
            "incident_id": incident_id,
            "category": incident["category"],
            "title": incident["title"],
            "resolution": incident["resolution"],
            "verified_by": actor,
        }
        _knowledge.append(entry)
        record(incident_id, "resolution_verified", actor)
        return entry.copy()


@app.get("/knowledge")
def list_knowledge():
    with _lock:
        return [item.copy() for item in _knowledge]


@app.get("/audit")
def audit_events():
    with _lock:
        return [item.copy() for item in _audit]


@app.get("/overview")
def overview():
    with _lock:
        return {
            "total_incidents": len(_incidents),
            "open": sum(i["status"] == "open" for i in _incidents.values()),
            "investigating": sum(i["status"] == "investigating" for i in _incidents.values()),
            "resolved": sum(i["status"] == "resolved" for i in _incidents.values()),
            "verified_knowledge_items": len(_knowledge),
        }
