"""Relational persistence foundation. Not wired to HTTP endpoints yet.

SQLite is supported for local schema tests; use PostgreSQL with migrations and
row-level security before multi-tenant production deployment.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON,
    String, Text, UniqueConstraint, create_engine, event
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    external_subject: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)


class Membership(Base):
    __tablename__ = "memberships"
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)
    __table_args__ = (CheckConstraint("role IN ('viewer','engineer','manager','approver','admin')", name="membership_role"),)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    assigned_team: Mapped[str | None] = mapped_column(String(100))
    resolution: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (
        CheckConstraint("priority BETWEEN 1 AND 4", name="incident_priority"),
        CheckConstraint("status IN ('open','investigating','resolved','closed')", name="incident_status"),
        Index("ix_incidents_tenant_status", "tenant_id", "status"),
    )


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    source_incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.id"), nullable=False)
    verified_by_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    resolution: Mapped[str] = mapped_column(Text, nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (UniqueConstraint("tenant_id", "source_incident_id", name="uq_knowledge_source"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    subject_type: Mapped[str] = mapped_column(String(60), nullable=False)
    subject_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (Index("ix_audit_tenant_time", "tenant_id", "occurred_at"),)


def make_engine(url: str | None = None):
    url = url or os.getenv("DATABASE_URL", "sqlite+pysqlite:///./opsentra-dev.db")
    engine = create_engine(url, pool_pre_ping=True)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    return engine


def make_session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)


def initialize_local_schema(engine):
    """Development only. Production schema changes require Alembic migrations."""
    Base.metadata.create_all(engine)
