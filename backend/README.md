# Demo backend

Run locally from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
PYTHONPATH=backend uvicorn app.main:app --reload
```

API docs: http://127.0.0.1:8000/docs

Tests: `PYTHONPATH=backend pytest backend/tests`

This is an unauthenticated in-memory prototype, **not production ready**.
