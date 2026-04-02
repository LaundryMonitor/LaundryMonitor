from typing import Any

import streamlit as st


MACHINES_STATE_KEY = "page_machines"
LOAD_ERROR_STATE_KEY = "page_load_error"


def read_page_state() -> tuple[list[dict[str, Any]], str | None]:
    """Read cached machines and the latest load error."""

    return st.session_state[MACHINES_STATE_KEY], st.session_state[LOAD_ERROR_STATE_KEY]


def store_page_state(machines: list[dict[str, Any]], load_error: str | None = None) -> None:
    """Store the latest machine snapshot in session state."""

    st.session_state[MACHINES_STATE_KEY] = machines
    st.session_state[LOAD_ERROR_STATE_KEY] = load_error
