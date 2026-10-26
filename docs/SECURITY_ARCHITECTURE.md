# OPSENTRA AI — Security Architecture (draft)

## Trust boundaries
- Each customer is a separate tenant; all records, connectors, search indexes and logs must be tenant-scoped.
- Customer systems are systems of record. Read-only integrations are the default.
- A deterministic workflow engine—not a language model—decides routing, authorization, approvals and escalation.
- The AI may draft recommendations; privileged actions require explicit policy authorization and, when configured, human approval.

## Required before any hosted deployment
1. OIDC authentication with validated issuer, audience, expiry and signature.
2. Tenant membership and role-based access control on every endpoint.
3. PostgreSQL storage with tenant_id on all tenant-owned tables and tested row-level security.
4. Append-only audit events, trusted actor identity, timestamps and trace IDs.
5. Secrets management; no credentials in source or logs.
6. Encrypted transport and storage; data retention/deletion controls.
7. Connector permissions limited to the approved scope; revocable tokens.
8. Approval policies, separation of duties and human sign-off for changes to permissions, purchases and production infrastructure.
9. Rate limits, input validation, logging, backups and recovery tests.
10. Security testing before onboarding customer data.

## Current prototype limitations
The current API is **not authenticated** and accepts unverified actor strings. Its records are **in memory** and **not tenant-isolated**. Its audit log is **not durable**. It must run only in an isolated local development environment with synthetic data. Never deploy it publicly.

## Design principle
An LLM response is untrusted content, not authority. Knowledge suggestions must cite verified internal evidence and never silently mutate source records.
