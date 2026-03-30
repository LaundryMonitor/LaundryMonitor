# Laundry Monitor (Phase 1)

Phase 1 includes:

- project skeleton with Poetry
- SQLite models and database initialization
- idempotent machine seed script
- pure backend status inference logic
- unit tests for inference logic

No API routes or frontend are implemented in this phase.

## Quick Start

```bash
poetry install
poetry run python scripts/init_db.py
poetry run python scripts/seed_machines.py
poetry run pytest
```
