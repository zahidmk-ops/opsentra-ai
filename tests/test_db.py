"""Schema tests: isolated SQLite only, not an authorization test."""
import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db import Base, Tenant, User, Membership, Incident, KnowledgeArticle, AuditEvent


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_tenant_incident_and_audit_persist(engine):
    with Session(engine) as session:
        tenant = Tenant(name="Demo Company")
        user = User(external_subject="test-idp|demo")
        session.add_all([tenant, user])
        session.flush()
        session.add(Membership(tenant_id=tenant.id, user_id=user.id, role="manager"))
        incident = Incident(
            tenant_id=tenant.id, title="Backup failed", description="Nightly job",
            category="backup", priority=1, assigned_team="Backup Operations"
        )
        session.add(incident)
        session.flush()
        session.add(AuditEvent(
            tenant_id=tenant.id, actor_user_id=user.id,
            action="created", subject_type="incident", subject_id=incident.id
        ))
        session.commit()
        incident_id = incident.id
        tenant_id = tenant.id
    with Session(engine) as session:
        stored = session.scalar(select(Incident).where(Incident.tenant_id == tenant_id))
        assert stored.id == incident_id
        assert stored.status == "open"
        assert session.scalar(select(AuditEvent)).action == "created"


def test_invalid_membership_role_rejected(engine):
    with Session(engine) as session:
        tenant = Tenant(name="Tenant B")
        user = User(external_subject="idp|b")
        session.add_all([tenant, user])
        session.flush()
        session.add(Membership(tenant_id=tenant.id, user_id=user.id, role="superuser"))
        with pytest.raises(IntegrityError):
            session.commit()


def test_cross_tenant_foreign_keys_are_not_sufficient_isolation(engine):
    """Documents a known gap: DB FKs alone do not enforce tenant matching."""
    assert "tenant_id" in Incident.__table__.columns
    # Must implement PostgreSQL RLS and tenant-scoped queries before exposing API.
