from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Literal
from uuid import uuid4

app = FastAPI(title="Opsentra AI API", version="0.1.0")

class IncidentCreate(BaseModel):
    title: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    service: str = "General IT"

class Incident(IncidentCreate):
    id: str
    status: Literal["open", "investigating", "resolved"] = "open"

# Demonstration-only in-memory data. Resets on restart.
incidents: dict[str, Incident] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "opsentra-api"}

@app.get("/api/v1/incidents", response_model=list[Incident])
def list_incidents():
    return list(incidents.values())

@app.post("/api/v1/incidents", response_model=Incident, status_code=201)
def create_incident(payload: IncidentCreate):
    incident = Incident(id=str(uuid4()), **payload.model_dump())
    incidents[incident.id] = incident
    return incident

@app.get("/api/v1/dashboard")
def dashboard():
    values = list(incidents.values())
    return {"total_incidents": len(values), "open_incidents": sum(i.status != "resolved" for i in values), "critical_incidents": sum(i.severity == "critical" and i.status != "resolved" for i in values), "mode": "demo"}

@app.patch("/api/v1/incidents/{incident_id}/resolve", response_model=Incident)
def resolve_incident(incident_id: str):
    incident = incidents.get(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident.status = "resolved"
    return incident
