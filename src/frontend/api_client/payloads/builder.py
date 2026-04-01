from frontend.api_client.payloads.parsing import parse_optional_non_negative_int


ALLOWED_REPORT_STATUSES = {"busy", "free", "unavailable"}


def build_report_payload(
    *,
    machine_id: int,
    status: str,
    time_remaining_text: str,
    reporter_name_text: str,
) -> dict[str, object]:
    """Build a validated report payload for backend submission."""

    # Validate the submitted status before constructing the payload.
    if status not in ALLOWED_REPORT_STATUSES:
        raise ValueError("Status must be one of: busy, free, unavailable.")

    # Start with fields that are always required by the backend.
    payload: dict[str, object] = {
        "machine_id": machine_id,
        "status": status,
    }

    # Include optional reporter metadata only when it was provided.
    reporter_name = reporter_name_text.strip()
    if reporter_name:
        payload["reporter_name"] = reporter_name

    # Include remaining time only for busy-machine reports.
    if status == "busy":
        time_remaining = parse_optional_non_negative_int(time_remaining_text)
        if time_remaining is not None:
            payload["time_remaining"] = time_remaining

    return payload
