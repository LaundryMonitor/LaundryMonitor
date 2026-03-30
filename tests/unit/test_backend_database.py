from __future__ import annotations

import asyncio

from sqlalchemy import create_engine, inspect, text

import backend.database as database_module


def test_get_database_url_from_env(monkeypatch) -> None:
    monkeypatch.setenv("LAUNDRY_MONITOR_DB_PATH", "/tmp/custom.db")

    assert database_module.get_database_url() == "sqlite:////tmp/custom.db"


def test_init_database_creates_tables() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    database_module.init_database(engine)
    inspector = inspect(engine)

    assert set(inspector.get_table_names()) == {"machines", "reports"}


def test_get_db_yields_session_and_closes(monkeypatch) -> None:
    class DummySession:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    dummy_session = DummySession()
    monkeypatch.setattr(database_module, "SessionLocal", lambda: dummy_session)

    async def _run() -> None:
        generator = database_module.get_db()
        session = await anext(generator)
        assert session is dummy_session
        await generator.aclose()
        assert dummy_session.closed is True

    asyncio.run(_run())


def test_normalize_legacy_enum_values() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    with engine.begin() as connection:
        connection.execute(
            text(
                "CREATE TABLE machines ("
                "id INTEGER PRIMARY KEY, "
                "name TEXT NOT NULL, "
                "type TEXT NOT NULL)"
            )
        )
        connection.execute(
            text(
                "CREATE TABLE reports ("
                "id INTEGER PRIMARY KEY, "
                "machine_id INTEGER NOT NULL, "
                "status TEXT NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO machines (id, name, type) VALUES "
                "(1, 'Washer 1', 'WASH')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO reports (id, machine_id, status) VALUES "
                "(1, 1, 'BUSY')"
            )
        )

    database_module._normalize_legacy_enum_values(engine)

    with engine.connect() as connection:
        machine_type = connection.execute(
            text("SELECT type FROM machines WHERE id = 1")
        ).scalar_one()
        report_status = connection.execute(
            text("SELECT status FROM reports WHERE id = 1")
        ).scalar_one()

    assert machine_type == "wash"
    assert report_status == "busy"
