# Opsentra AI

**Powered by PGU Systems**

Opsentra AI is a planned commercial, multi-client AI application platform.

## Initial engineering principles
- Separate each client's data and configuration.
- Require authenticated access and role-based permissions.
- Keep API keys and credentials out of Git.
- Collect and process customer data only with appropriate authorization.
- Log important actions without exposing sensitive data.
- Build a small working MVP before adding modules.

## Project status
Repository initialized. Product requirements and first MVP workflow are being finalized. No production functionality is implemented yet.

## Proposed next steps
1. Confirm the exact first customer workflow and success criteria.
2. Select the smallest implementation stack and data model.
3. Implement API, authentication, and tenant isolation.
4. Add automated tests and a demonstration environment.

## Security
Never commit customer records, passwords, API keys, or production environment files. Use environment variables and managed secrets.
