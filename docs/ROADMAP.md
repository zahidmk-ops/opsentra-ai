# Opsentra AI MVP roadmap

## Product
Enterprise IT Intelligence & Automation Platform — Powered by PGU Systems.

## MVP modules
1. IT Command Dashboard
2. Incident workflow (human-controlled)
3. AI Knowledge Assistant grounded in approved SOPs and incidents
4. Executive reporting

## Stage 1 — demo API
- [x] Incident CRUD subset and dashboard summary (in-memory)
- [x] Automated API tests configured
- [ ] Next.js command center frontend

## Stage 2 — persistence and controls
- [ ] PostgreSQL with tenant-scoped tables
- [ ] Authentication, RBAC, and tenant isolation tests
- [ ] Audit logs and approval gates

## Stage 3 — AI and reporting
- [ ] Permission-aware SOP retrieval
- [ ] Verified answer citations and abstention
- [ ] Executive report generation

## Security gate
Demo API has no authentication and MUST NOT be publicly deployed or connected to real customer data. No production credentials in source control.
