from __future__ import annotations

from typing import Any

import httpx
import pytest

import frontend.api_client as api_client_module
import frontend.page.flash as page_flash_module
import frontend.report_form.submission as submission_module
from frontend.api_client import (
    BackendResponseError,
    BackendUnavailableError,
    LaundryAPIClient,
    build_report_payload,
    parse_optional_non_negative_int,
)
from frontend.config import DEFAULT_BACKEND_URL, get_backend_base_url
from frontend.report_form.submission import submit_report_form


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


def test_build_report_payload_ignores_blank_reporter_name_for_busy() -> None:
    payload = build_report_payload(
        machine_id=3,
        status="busy",
        time_remaining_text="5",
        reporter_name_text="   ",
    )

    assert payload == {
        "machine_id": 3,
        "status": "busy",
        "time_remaining": 5,
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


def test_client_get_machine_history_uses_default_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    response = httpx.Response(200, json=[])
    stub_client = StubHTTPXClient(response=response)
    monkeypatch.setattr(
        api_client_module.httpx,
        "Client",
        StubHTTPXClientFactory(stub_client),
    )

    client = LaundryAPIClient("http://backend:8000")
    history = client.get_machine_history(machine_id=2)

    assert history == []
    assert stub_client.requests[0]["params"] == {"limit": 5}


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


def test_get_machines_raises_on_unexpected_payload_type(
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
        client.get_machines()


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


class StubSubmissionClient:
    def __init__(
        self,
        *,
        submit_response: dict[str, Any],
        machines_response: list[dict[str, Any]] | None = None,
        machines_error: Exception | None = None,
    ) -> None:
        self.submit_response = submit_response
        self.machines_response = machines_response or []
        self.machines_error = machines_error
        self.submitted_payload: dict[str, Any] | None = None

    def submit_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.submitted_payload = payload
        return self.submit_response

    def get_machines(self) -> list[dict[str, Any]]:
        if self.machines_error is not None:
            raise self.machines_error
        return self.machines_response


def test_pop_flash_messages_clears_session(monkeypatch: pytest.MonkeyPatch) -> None:
    session_state = {
        page_flash_module.FLASH_SUCCESS_KEY: "Saved.",
        page_flash_module.FLASH_ERROR_KEY: "Failed.",
    }
    monkeypatch.setattr(page_flash_module.st, "session_state", session_state, raising=False)

    flash_success, flash_error = page_flash_module.pop_flash_messages()

    assert flash_success == "Saved."
    assert flash_error == "Failed."
    assert session_state == {}


def test_submit_report_form_returns_refreshed_machines(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reset_calls: list[str] = []
    monkeypatch.setattr(
        submission_module,
        "reset_report_form_state",
        lambda: reset_calls.append("reset"),
    )
    client = StubSubmissionClient(
        submit_response={"id": 7},
        machines_response=[{"id": 1, "inferred_status": "busy"}],
    )

    submit_message, submit_error, machines = submit_report_form(
        client,
        machine_id=1,
        status="busy",
        time_remaining_text="35",
        reporter_name_text=" Polina ",
        machines=[{"id": 1, "inferred_status": "free"}],
    )

    assert client.submitted_payload == {
        "machine_id": 1,
        "status": "busy",
        "time_remaining": 35,
        "reporter_name": "Polina",
    }
    assert reset_calls == ["reset"]
    assert submit_message == "Report #7 submitted successfully."
    assert submit_error is None
    assert machines == [{"id": 1, "inferred_status": "busy"}]


def test_submit_report_form_when_refresh_fails_shows_only_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When report saves but refresh fails, show only error message (no success)."""
    reset_calls: list[str] = []
    monkeypatch.setattr(
        submission_module,
        "reset_report_form_state",
        lambda: reset_calls.append("reset"),
    )
    client = StubSubmissionClient(
        submit_response={"id": 9},
        machines_error=BackendUnavailableError("Backend offline"),
    )
    old_machines = [{"id": 1, "inferred_status": "free"}]

    submit_message, submit_error, machines = submit_report_form(
        client,  # type: ignore[arg-type]
        machine_id=1,
        status="free",
        time_remaining_text="",
        reporter_name_text="",
        machines=old_machines,
    )

    # Report was saved, so success message should NOT appear
    assert submit_message is None
    # Only error message appears, clearly indicating what to do
    assert submit_error is not None
    assert "saved successfully" in submit_error
    assert "click 'Refresh'" in submit_error
    assert "Report #9" in submit_error
    # Dashboard shows stale data (old machines), user must refresh
    assert machines == old_machines

