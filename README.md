# Laundry Monitor (Phase 1)

Current project state includes:

- project skeleton with Poetry
- SQLite models and database initialization
- idempotent machine seed script
- pure backend status inference logic
- FastAPI app with report/machine endpoints
- unit and integration tests

No Streamlit frontend is implemented yet.

## Quick Start

```bash
poetry install
poetry run python scripts/init_db.py
poetry run python scripts/seed_machines.py
poetry run uvicorn backend.main:app --reload
poetry run pytest
```
