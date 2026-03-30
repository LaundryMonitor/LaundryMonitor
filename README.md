# Laundry Monitor

Current project state includes:

- FastAPI backend with SQLite and status inference
- Streamlit frontend that consumes backend API endpoints
- idempotent machine seed script
- unit and integration tests

## Configuration

- `LAUNDRY_MONITOR_API_URL`:
  backend base URL for frontend
  default: `http://127.0.0.1:8000`

## Run Backend

```bash
poetry install
poetry run python scripts/init_db.py
poetry run python scripts/seed_machines.py
poetry run uvicorn backend.main:app --reload
```

## Run Frontend

```bash
poetry run streamlit run src/frontend/app.py
```

If backend is running on another host/port:

```bash
LAUNDRY_MONITOR_API_URL=http://127.0.0.1:8001 poetry run streamlit run src/frontend/app.py
```

## Run Tests

```bash
poetry run pytest
```
