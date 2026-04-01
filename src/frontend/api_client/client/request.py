from __future__ import annotations

from typing import Any

import httpx

from frontend.api_client.errors import BackendResponseError, BackendUnavailableError
from frontend.api_client.response_parsing import extract_error_detail


def request_json(
    *,
    base_url: str,
    timeout_seconds: float,
    method: str,
    path: str,
    expected_status_code: int,
    action_description: str,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    """Send one backend request and validate the JSON response."""

    url = f"{base_url}{path}"
    try:
        with httpx.Client(timeout=timeout_seconds) as client:
            response = client.request(method=method, url=url, json=json, params=params)
    except httpx.RequestError as exc:
        raise BackendUnavailableError(
            f"Could not reach backend at {base_url}. "
            f"Make sure backend is running and URL is correct."
        ) from exc

    if response.status_code != expected_status_code:
        error_detail = extract_error_detail(response)
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
