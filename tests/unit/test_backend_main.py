from __future__ import annotations

import asyncio

import backend.main as backend_main


def test_lifespan_initializes_database(monkeypatch) -> None:
    calls = {"count": 0}

    def fake_init_database() -> None:
        calls["count"] += 1

    monkeypatch.setattr(backend_main, "init_database", fake_init_database)

    async def _run() -> None:
        async with backend_main.lifespan(backend_main.app):
            pass

    asyncio.run(_run())

    assert calls["count"] == 1
