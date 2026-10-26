# Database foundation

SQLAlchemy schema in `app/db.py` defines tenants, identity subjects, memberships,
incidents, verified knowledge, and audit events.

This schema is **not yet connected to API handlers**. Existing HTTP endpoints still
use in-memory demo dictionaries. No authentication or tenant enforcement exists.

## Local schema creation
```bash
python -c "from app.db import make_engine, initialize_local_schema; initialize_local_schema(make_engine())"
```
This creates a local SQLite file for development only. The file is not encrypted.

## Production blockers
- Add Alembic migrations and PostgreSQL deployment.
- Implement OIDC verification, authenticated actor identity and role enforcement.
- Add PostgreSQL RLS with tenant-aware transaction context; test tenant isolation.
- Validate cross-tenant references in application logic and database constraints.
- Protect audit history against modification, and add retention policy.
- Replace the in-memory API stores with scoped repository methods.
- Add secrets management, backups, recovery tests and deployment hardening.

Do not use real customer records in the current prototype.
