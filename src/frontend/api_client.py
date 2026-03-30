from __future__ import annotations

from typing import Any

import httpx


ALLOWED_REPORT_STATUSES = {"busy", "free", "unavailable"}


class FrontendAPIError(Exception):
    """Base error for frontend/backend API communication."""


class BackendUnavailableError(FrontendAPIError):
    """Raised when backend cannot be reached."""


class BackendResponseError(FrontendAPIError):
    """Raised when backend responds with an unexpected HTTP status."""


class LaundryAPIClient:
    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_machines(self) -> list[dict[str, Any]]:
        data = self._request_json(
            method="GET",
            path="/machines",
            expected_status_code=200,
            action_description="load machines",
        )
        if not isinstance(data, list):
            raise BackendResponseError("Backend returned unexpected data for /machines.")
        return data

    def submit_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = self._request_json(
            method="POST",
            path="/report",
            expected_status_code=201,
            action_description="submit report",
            json=payload,
        )
        if not isinstance(data, dict):
            raise BackendResponseError("Backend returned unexpected data for /report.")
        return data

    def get_machine_history(self, machine_id: int, limit: int = 5) -> list[dict[str, Any]]:
        data = self._request_json(
            method="GET",
            path=f"/machines/{machine_id}/history",
            expected_status_code=200,
            action_description="load machine history",
            params={"limit": limit},
        )
        if not isinstance(data, list):
            raise BackendResponseError("Backend returned unexpected data for machine history.")
        return data

    def _request_json(
        self,
        *,
        method: str,
        path: str,
        expected_status_code: int,
        action_description: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.request(method=method, url=url, json=json, params=params)
        except httpx.RequestError as exc:
            raise BackendUnavailableError(
                f"Could not reach backend at {self.base_url}. "
                f"Make sure backend is running and URL is correct."
            ) from exc

        if response.status_code != expected_status_code:
            error_detail = _extract_error_detail(response)
            raise BackendResponseError(
                f"Backend error while trying to {action_description}: "
                f"HTTP {response.status_code}. {error_detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise BackendResponseError(
                f"Backend returned invalid JSON while trying to {action_description}."
            ) from exc


def build_report_payload(
    *,
    machine_id: int,
    status: str,
    time_remaining_text: str,
    reporter_name_text: str,
) -> dict[str, Any]:
    if status not in ALLOWED_REPORT_STATUSES:
        raise ValueError("Status must be one of: busy, free, unavailable.")

    payload: dict[str, Any] = {
        "machine_id": machine_id,
        "status": status,
    }

    reporter_name = reporter_name_text.strip()
    if reporter_name:
        payload["reporter_name"] = reporter_name

    if status == "busy":
        time_remaining = parse_optional_non_negative_int(time_remaining_text)
        if time_remaining is not None:
            payload["time_remaining"] = time_remaining

    return payload


def parse_optional_non_negative_int(raw_value: str) -> int | None:
    value = raw_value.strip()
    if not value:
        return None
    if not value.isdigit():
        raise ValueError("Time remaining must be a non-negative integer.")
    return int(value)


def _extract_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        text = response.text.strip()
        return text if text else "No error details were provided."

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        if detail is not None:
            return str(detail)

    return "No error details were provided."
