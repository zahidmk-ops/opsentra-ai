"""Tests for the local persistence service (not an authorization/security test)."""
import pytest
from sqlalchemy import create_engine, select, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, Tenant, AuditEvent
from app.incident_service import create_incident, list_incidents, change_status, WorkflowError


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    @event.listens_for(engine, "connect")
    def enable_fk(dbapi_connection, _):
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add_all([Tenant(id="tenant-a", name="A"), Tenant(id="tenant-b", name="B")])
        db.commit()
        yield db
    engine.dispose()


def test_incident_is_tenant_scoped_and_audited(session):
    item = create_incident(session, tenant_id="tenant-a", title="Backup failed",
                           description="Nightly backup failure", category="backup", priority=1)
    assert [x.id for x in list_incidents(session, tenant_id="tenant-a")] == [item.id]
    assert list_incidents(session, tenant_id="tenant-b") == []
    assert session.scalar(select(AuditEvent)).action == "incident_created"
    with pytest.raises(WorkflowError):
        change_status(session, tenant_id="tenant-b", incident_id=item.id, status="investigating")


def test_resolution_requires_documentation_and_order(session):
    item = create_incident(session, tenant_id="tenant-a", title="Server down",
                           description="Host unavailable", category="server", priority=2)
    with pytest.raises(WorkflowError):
        change_status(session, tenant_id="tenant-a", incident_id=item.id, status="closed")
    change_status(session, tenant_id="tenant-a", incident_id=item.id, status="investigating")
    with pytest.raises(WorkflowError):
        change_status(session, tenant_id="tenant-a", incident_id=item.id, status="resolved")
    change_status(session, tenant_id="tenant-a", incident_id=item.id, status="resolved",
                  resolution="Restarted service and verified recovery")
    closed = change_status(session, tenant_id="tenant-a", incident_id=item.id, status="closed")
    assert closed.status == "closed"
    assert len(list(session.scalars(select(AuditEvent)))) == 4
