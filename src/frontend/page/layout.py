from typing import Any

import streamlit as st

from frontend.config import BACKEND_URL_ENV_VAR, get_backend_base_url
from frontend.ui import render_machine_grid


def render_page_header() -> tuple[str, bool]:
    """Render the page header and return basic page controls."""

    st.set_page_config(page_title="Laundry Monitor", layout="wide")
    st.title("Laundry Monitor")

    backend_url = get_backend_base_url()
    st.caption(
        f"Backend URL: `{backend_url}` "
        f"(override with `{BACKEND_URL_ENV_VAR}` environment variable)."
    )
    refresh_requested = st.button("Refresh")
    return backend_url, refresh_requested


def render_feedback(
    *,
    flash_success: str | None,
    flash_error: str | None,
    submit_message: str | None,
    submit_error: str | None,
) -> None:
    """Render feedback below the report form."""

    feedback_placeholder = st.empty()
    with feedback_placeholder.container():
        if flash_success:
            st.success(flash_success)
        if flash_error:
            st.error(flash_error)
        if submit_message:
            st.success(submit_message)
        if submit_error:
            st.error(submit_error)


def render_load_error(load_error: str | None) -> None:
    """Render the current backend loading error when one exists."""

    if load_error:
        st.error(load_error)


def render_dashboard(machines: list[dict[str, Any]], load_error: str | None) -> None:
    """Render the dashboard or an unavailable notice."""

    if load_error:
        st.info("Machine dashboard is unavailable until backend data can be loaded.")
        return

    render_machine_grid(machines)
