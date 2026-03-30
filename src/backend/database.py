from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
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


def init_database() -> None:
    # Imported here to make sure models are registered before create_all.
    import backend.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
