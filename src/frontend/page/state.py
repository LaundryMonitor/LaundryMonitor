from typing import Any

import streamlit as st

from frontend.api_client import LaundryAPIClient
from frontend.loader import load_machines
from frontend.page.cache import MACHINES_STATE_KEY, read_page_state, store_page_state


def load_page_state(
    client: LaundryAPIClient,
    *,
    refresh_requested: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    """Load cached machines or refresh them from the backend."""

    if refresh_requested or MACHINES_STATE_KEY not in st.session_state:
        machines, load_error = load_machines(client)
        store_page_state(machines, load_error)
        return machines, load_error

    return read_page_state()
