from __future__ import annotations

from typing import Any

from frontend.api_client import BackendResponseError, BackendUnavailableError, LaundryAPIClient


def load_machines(client: LaundryAPIClient) -> tuple[list[dict[str, Any]], str | None]:
    """Fetch machines and normalize backend errors for the frontend."""

    try:
        machines = client.get_machines()
    except (BackendUnavailableError, BackendResponseError) as exc:
        return [], str(exc)
    return machines, None
