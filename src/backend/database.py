from __future__ import annotations

import os
from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase, sessionmaker


DEFAULT_DB_PATH = Path("laundry_monitor.db")


def get_database_url() -> str:
    db_path = os.getenv("LAUNDRY_MONITOR_DB_PATH", str(DEFAULT_DB_PATH))
    return f"sqlite:///{db_path}"


class Base(DeclarativeBase):
    pass


engine = create_engine(
    get_database_url(),
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_database(db_engine: Engine | None = None) -> None:
    target_engine = db_engine or engine

    # Imported here to make sure models are registered before create_all.
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=target_engine)
    _normalize_legacy_enum_values(target_engine)


async def get_db() -> AsyncIterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _normalize_legacy_enum_values(db_engine: Engine) -> None:
    # Backward-compatible cleanup for early local DBs that stored uppercase enum names.
    with db_engine.begin() as connection:
        connection.exec_driver_sql(
            "UPDATE machines SET type = lower(type) WHERE type IN ('WASH', 'DRY')"
        )
        connection.exec_driver_sql(
            "UPDATE reports SET status = lower(status) "
            "WHERE status IN ('BUSY', 'FREE', 'UNAVAILABLE')"
        )
