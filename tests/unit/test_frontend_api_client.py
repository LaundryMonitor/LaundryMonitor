from __future__ import annotations

from typing import Any

import httpx
import pytest

import frontend.api_client as api_client_module
from frontend.api_client import (
    BackendResponseError,
    BackendUnavailableError,
    LaundryAPIClient,
    build_report_payload,
    parse_optional_non_negative_int,
)
from frontend.config import DEFAULT_BACKEND_URL, get_backend_base_url


class StubHTTPXClient:
    def __init__(
        self,
        *,
        response: httpx.Response | None = None,
        request_error: Exception | None = None,
    ) -> None:
        self.response = response
        self.request_error = request_error
        self.requests: list[dict[str, Any]] = []

    def __enter__(self) -> StubHTTPXClient:
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def request(
        self,
        *,
        method: str,
        url: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "json": json,
                "params": params,
            }
        )
        if self.request_error is not None:
            raise self.request_error
        assert self.response is not None
        return self.response


class StubHTTPXClientFactory:
    def __init__(self, client: StubHTTPXClient) -> None:
        self.client = client
        self.timeout: float | None = None

    def __call__(self, *, timeout: float) -> StubHTTPXClient:
        self.timeout = timeout
        return self.client


def test_build_report_payload_for_busy_with_time_remaining() -> None:
    payload = build_report_payload(
        machine_id=2,
        status="busy",
        time_remaining_text="35",
        reporter_name_text=" Polina ",
    )

    assert payload == {
        "machine_id": 2,
        "status": "busy",
        "time_remaining": 35,
        "reporter_name": "Polina",
    }


def test_build_report_payload_ignores_time_for_non_busy_status() -> None:
    payload = build_report_payload(
        machine_id=1,
        status="free",
        time_remaining_text="25",
        reporter_name_text="",
    )

    assert payload == {
        "machine_id": 1,
        "status": "free",
    }


def test_build_report_payload_rejects_invalid_status() -> None:
    with pytest.raises(ValueError):
        build_report_payload(
            machine_id=1,
            status="invalid",
            time_remaining_text="",
            reporter_name_text="",
        )


def test_parse_optional_non_negative_int() -> None:
    assert parse_optional_non_negative_int("") is None
    assert parse_optional_non_negative_int("12") == 12

    with pytest.raises(ValueError):
        parse_optional_non_negative_int("-1")

    with pytest.raises(ValueError):
        parse_optional_non_negative_int("abc")


def test_get_backend_base_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LAUNDRY_MONITOR_API_URL", raising=False)
    assert get_backend_base_url() == DEFAULT_BACKEND_URL

    monkeypatch.setenv("LAUNDRY_MONITOR_API_URL", "http://backend:9000/")
    assert get_backend_base_url() == "http://backend:9000"


def test_client_get_machines_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(200, json=[{"id": 1}])
    stub_client = StubHTTPXClient(response=response)
    stub_factory = StubHTTPXClientFactory(stub_client)
    monkeypatch.setattr(api_client_module.httpx, "Client", stub_factory)

    client = LaundryAPIClient("http://backend:8000", timeout_seconds=7.0)
    machines = client.get_machines()

    assert machines == [{"id": 1}]
    assert stub_factory.timeout == 7.0
    assert stub_client.requests == [
        {
            "method": "GET",
            "url": "http://backend:8000/machines",
            "json": None,
            "params": None,
        }
    ]


def test_client_get_machine_history_success(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(200, json=[{"id": 4, "machine_id": 1}])
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )

    client = LaundryAPIClient("http://backend:8000")
    history = client.get_machine_history(machine_id=1, limit=3)

    assert history == [{"id": 4, "machine_id": 1}]
    assert stub_client.requests[0]["params"] == {"limit": 3}


def test_submit_report_raises_on_unexpected_payload_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = httpx.Response(201, json=["unexpected"])
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendResponseError):
        client.submit_report({"machine_id": 1, "status": "busy"})


def test_machine_history_raises_on_unexpected_payload_type(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = httpx.Response(200, json={"unexpected": True})
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendResponseError):
        client.get_machine_history(machine_id=1)


def test_request_error_raises_backend_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    connect_error = httpx.ConnectError(
        "connection failed",
        request=httpx.Request("GET", "http://backend:8000/machines"),
    )
    stub_client = StubHTTPXClient(request_error=connect_error)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendUnavailableError):
        client.get_machines()


def test_backend_response_error_uses_string_detail(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(404, json={"detail": "Machine 1 not found"})
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendResponseError, match="Machine 1 not found"):
        client.get_machines()


def test_backend_response_error_uses_non_json_text(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(500, text="internal error")
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendResponseError, match="internal error"):
        client.get_machines()


def test_backend_response_error_invalid_json_body(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(200, text="not-json")
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )
    client = LaundryAPIClient("http://backend:8000")

    with pytest.raises(BackendResponseError, match="invalid JSON"):
        client.get_machines()
