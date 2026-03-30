# Laundry Monitor

Local web app for dormitory students to report and view laundry machine status.

## Project Overview

Laundry Monitor has two runtime services:

- FastAPI backend (status reporting, status inference, machine history)
- Streamlit frontend (dashboard + report form)

Status inference logic lives in backend domain code and is the single source of truth.

## Architecture Summary

- `src/backend/`
  - API routes (`/report`, `/machines`, `/machines/{id}/history`)
  - service layer + domain inference logic
  - SQLite via SQLAlchemy
- `src/frontend/`
  - Streamlit UI
  - API client that calls backend over HTTP
- `scripts/`
  - `init_db.py` to create DB tables
  - `seed_machines.py` to insert default machines idempotently
- `tests/`
  - unit + integration tests
  - minimal locust smoke test in `tests/load/`
- Docker
  - backend and frontend containers in `compose.yml`
  - persistent named volume for SQLite data

## Tech Stack

- Python 3.11+
- FastAPI + Uvicorn
- Streamlit
- SQLAlchemy + SQLite
- Poetry
- Pytest, Flake8, Radon, Bandit, Locust

## Environment Variables

- `LAUNDRY_MONITOR_DB_PATH`
  - SQLite file path for backend
  - local default: `laundry_monitor.db`
  - docker value: `/data/laundry_monitor.db`
- `LAUNDRY_MONITOR_API_URL`
  - backend URL used by frontend
  - local default: `http://127.0.0.1:8000`
  - docker value: `http://backend:8000`

## Local Setup (Non-Docker)

Install dependencies:

```bash
poetry install
```

Initialize and seed database:

```bash
poetry run python scripts/init_db.py
poetry run python scripts/seed_machines.py
```

Run backend:

```bash
poetry run uvicorn backend.main:app --reload
```

Run frontend (in another terminal):

```bash
poetry run streamlit run src/frontend/app.py
```

If backend is on another URL:

```bash
LAUNDRY_MONITOR_API_URL=http://127.0.0.1:8001 poetry run streamlit run src/frontend/app.py
```

## Docker Setup

Build and start both services:

```bash
docker compose up --build -d
```

Stop containers:

```bash
docker compose down
```

Backend auto-initializes tables on startup. Seed is manual:

```bash
docker compose exec backend poetry run python scripts/seed_machines.py
```

Optional manual init command:

```bash
docker compose exec backend poetry run python scripts/init_db.py
```

Access:

- Backend docs: `http://127.0.0.1:8000/docs`
- Frontend UI: `http://127.0.0.1:8501`

SQLite persistence in Docker:

- DB file path: `/data/laundry_monitor.db`
- named volume: `laundry_monitor_data`

## Testing

Run all tests:

```bash
poetry run pytest
```

Run tests with coverage gate (>= 70%):

```bash
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
```

## Quality Checks

```bash
poetry check
poetry run flake8 src/ tests/
poetry run pytest
poetry run pytest --cov=src --cov-report=term-missing --cov-fail-under=70
poetry run radon cc src/ -a -s
poetry run python scripts/check_complexity.py
poetry run radon mi src/ -s
poetry run bandit -r src/ -ll
```

Locust smoke (requires backend running and machines seeded):

```bash
poetry run locust -f tests/load/locustfile.py --headless -u 1 -r 1 -t 10s
```

## Assumptions and Simplifications

- SQLite is the only database engine in this project.
- No authentication/authorization in current scope.
- Seed script is idempotent by machine name.
- Frontend never computes status inference; backend returns inferred status.
- Load test is a lightweight smoke scenario, not a performance benchmark.

## Troubleshooting

- Frontend shows backend unavailable:
  verify backend is running and `LAUNDRY_MONITOR_API_URL` is correct.
- Empty machine dashboard:
  run seed script and refresh UI.
- Docker data seems missing:
  check that compose volume `laundry_monitor_data` still exists and containers were not started with a different project name.
