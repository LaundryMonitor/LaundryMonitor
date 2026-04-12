from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import backend.models  # noqa: F401
from backend.database import Base, get_db
from backend.main import app


class SyncASGIClient:
    def __init__(self, base_url: str = "http://test") -> None:
        self._base_url = base_url

    def request(self, method: str, url: str, **kwargs: object) -> httpx.Response:
        async def _send() -> httpx.Response:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url=self._base_url) as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(_send())

    def get(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: object) -> httpx.Response:
        return self.request("POST", url, **kwargs)


@pytest.fixture
def session_factory(tmp_path: Path) -> sessionmaker[Session]:
    db_file = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    testing_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    yield testing_session_factory

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Generator[SyncASGIClient, None, None]:
    async def override_get_db() -> AsyncGenerator[Session, None]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield SyncASGIClient()
    app.dependency_overrides.clear()
