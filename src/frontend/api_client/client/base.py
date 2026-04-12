from __future__ import annotations

from typing import Any

from frontend.api_client.client.request import request_json
from frontend.api_client.errors import BackendResponseError


class LaundryAPIClient:
    """Synchronous frontend client for backend API requests."""

    def __init__(self, base_url: str, timeout_seconds: float = 5.0) -> None:
        """Store the backend base URL and request timeout."""

        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def get_machines(self) -> list[dict[str, Any]]:
        """Fetch all machines with inferred current statuses."""

        # Request the machine dashboard payload from the backend.
        data = request_json(
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
            method="GET",
            path="/machines",
            expected_status_code=200,
            action_description="load machines",
        )
        # Ensure the backend returned the expected collection shape.
        if not isinstance(data, list):
            raise BackendResponseError("Backend returned unexpected data for /machines.")
        return data

    def submit_report(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit one machine report to the backend API."""

        # Submit the user report and expect a created report object back.
        data = request_json(
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
            method="POST",
            path="/report",
            expected_status_code=201,
            action_description="submit report",
            json=payload,
        )
        # Guard against malformed backend responses.
        if not isinstance(data, dict):
            raise BackendResponseError("Backend returned unexpected data for /report.")
        return data

    def get_machine_history(self, machine_id: int, limit: int = 5) -> list[dict[str, Any]]:
        """Fetch recent report history for one machine."""

        # Request the recent history slice for one machine.
        data = request_json(
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
            method="GET",
            path=f"/machines/{machine_id}/history",
            expected_status_code=200,
            action_description="load machine history",
            params={"limit": limit},
        )
        # Ensure history is returned as a list of report objects.
        if not isinstance(data, list):
            raise BackendResponseError("Backend returned unexpected data for machine history.")
        return data
