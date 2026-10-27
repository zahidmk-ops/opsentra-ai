"""Local development persistence service; not an authenticated multi-tenant API.

Every operation requires an explicit tenant identifier. This is defense-in-depth
for local testing, NOT a substitute for authentication or PostgreSQL RLS.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import AuditEvent, Incident, Tenant

ALLOWED_CATEGORIES = {
    "network": "Network Operations",
    "server": "Systems Administration",
    "backup": "Backup Operations",
    "security": "Security Operations",
    "erp": "ERP Support",
    "endpoint": "IT Service Desk",
}
ALLOWED_TRANSITIONS = {
    "open": {"investigating"},
    "investigating": {"resolved"},
    "resolved": {"investigating", "closed"},
    "closed": set(),
}


class WorkflowError(ValueError):
    pass


def create_incident(session: Session, *, tenant_id: str, title: str,
                    description: str, category: str, priority: int,
                    actor_user_id: str | None = None) -> Incident:
    category = category.strip().lower()
    if category not in ALLOWED_CATEGORIES or not 1 <= priority <= 4:
        raise WorkflowError("Invalid incident category or priority")
    if not title.strip() or not description.strip():
        raise WorkflowError("Title and description are required")
    if session.get(Tenant, tenant_id) is None:
        raise WorkflowError("Unknown tenant")
    incident = Incident(tenant_id=tenant_id, title=title.strip(),
                        description=description.strip(), category=category,
                        priority=priority, assigned_team=ALLOWED_CATEGORIES[category])
    session.add(incident)
    session.flush()
    session.add(AuditEvent(tenant_id=tenant_id, actor_user_id=actor_user_id,
                           action="incident_created", subject_type="incident",
                           subject_id=incident.id))
    session.commit()
    session.refresh(incident)
    return incident


def list_incidents(session: Session, *, tenant_id: str) -> list[Incident]:
    return list(session.scalars(
        select(Incident).where(Incident.tenant_id == tenant_id)
        .order_by(Incident.created_at.desc(), Incident.id.desc())
    ))


def change_status(session: Session, *, tenant_id: str, incident_id: str,
                  status: str, resolution: str | None = None,
                  actor_user_id: str | None = None) -> Incident:
    incident = session.scalar(select(Incident).where(
        Incident.id == incident_id, Incident.tenant_id == tenant_id))
    if incident is None:
        raise WorkflowError("Incident not found for tenant")
    if status not in ALLOWED_TRANSITIONS[incident.status]:
        raise WorkflowError("Invalid status transition")
    if status == "resolved" and not (resolution and resolution.strip()):
        raise WorkflowError("Documented resolution required")
    if resolution is not None:
        incident.resolution = resolution.strip()
    incident.status = status
    session.add(AuditEvent(tenant_id=tenant_id, actor_user_id=actor_user_id,
                           action=f"status_changed_to_{status}",
                           subject_type="incident", subject_id=incident.id))
    session.commit()
    session.refresh(incident)
    return incident
