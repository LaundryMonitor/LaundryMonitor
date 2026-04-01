from __future__ import annotations

from typing import Any

from frontend.api_client import (
    BackendResponseError,
    BackendUnavailableError,
    LaundryAPIClient,
    build_report_payload,
)


def submit_report_form(
    client: LaundryAPIClient,
    *,
    machine_id: int,
    status: str,
    time_remaining_text: str,
    reporter_name_text: str,
    machines: list[dict[str, Any]],
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    """Submit a report and refresh machines for the frontend."""

    try:
        payload = build_report_payload(
            machine_id=machine_id,
            status=status,
            time_remaining_text=time_remaining_text,
            reporter_name_text=reporter_name_text,
        )
        response_data = client.submit_report(payload)
    except ValueError as exc:
        return None, str(exc), machines
    except (BackendUnavailableError, BackendResponseError) as exc:
        return None, str(exc), machines

    try:
        refreshed_machines = client.get_machines()
    except (BackendUnavailableError, BackendResponseError) as exc:
        return (
            f"Report #{response_data['id']} submitted.",
            f"Report was submitted, but machine refresh failed: {exc}",
            machines,
        )

    return f"Report #{response_data['id']} submitted.", None, refreshed_machines
