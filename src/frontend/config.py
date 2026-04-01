from __future__ import annotations

import os


BACKEND_URL_ENV_VAR = "LAUNDRY_MONITOR_API_URL"
DEFAULT_BACKEND_URL = "http://127.0.0.1:8000"


def get_backend_base_url() -> str:
    """Read and normalize the frontend backend base URL."""

    configured_url = os.getenv(BACKEND_URL_ENV_VAR, DEFAULT_BACKEND_URL)
    return configured_url.rstrip("/")
