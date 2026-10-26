# OPSENTRA AI
**Enterprise IT Intelligence & Automation**  
Powered by PGU Systems

An enterprise intelligence and workflow coordination layer complementing existing ITSM, infrastructure monitoring, cybersecurity and ERP systems.

## Status: local development prototype
The FastAPI backend currently supports:
- Incident intake, priorities and fixed demonstration team routing
- Incident resolution capture and human verification
- Verified knowledge records and audit events
- Summary overview endpoint

**Not production ready:** in-memory records, no authentication, tenant isolation, database, real AI, monitoring integrations, approvals or notifications. Do not expose to the internet or load customer data.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Windows activation: `.venv\\Scripts\\activate`.

API docs: http://127.0.0.1:8000/docs

## Roadmap
1. PostgreSQL, authentication, RBAC, tenant isolation, durable audit logs
2. Configurable routing, escalation, human approval workflows
3. Read-only ITSM and monitoring connectors
4. Source-grounded AI knowledge retrieval
5. Executive dashboards, evidence-backed reporting
6. Tests, security review and authorized customer pilot

## Security
Keep customer data in approved systems where possible; use explicit access grants, least privilege, approved retention, and audit trails. Never commit secrets or customer records.
