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
- `LAUNDRY_MONITOR_DB_PATH`:
  SQLite file path used by backend
  default (local run): `laundry_monitor.db`
  docker compose value: `/data/laundry_monitor.db`

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

## Run With Docker Compose

Build and start both services:

```bash
docker compose up --build -d
```

Stop services:

```bash
docker compose down
```

The backend automatically initializes tables on startup.
Machine seeding stays manual:

```bash
docker compose exec backend poetry run python scripts/seed_machines.py
```

Optional manual DB init command:

```bash
docker compose exec backend poetry run python scripts/init_db.py
```

Access points on host:

- Backend docs: `http://127.0.0.1:8000/docs`
- Streamlit UI: `http://127.0.0.1:8501`

SQLite persistence:

- Database file path in container: `/data/laundry_monitor.db`
- Persistent named volume: `laundry_monitor_data`
