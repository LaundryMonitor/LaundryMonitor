from __future__ import annotations

import httpx


def extract_error_detail(response: httpx.Response) -> str:
    """Extract a readable error message from backend responses."""

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
