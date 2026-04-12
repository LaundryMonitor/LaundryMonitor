from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui.card.actions import queue_report_as_free
from frontend.ui.card.details import render_machine_details


def render_machine_card(machine: dict[str, Any]) -> None:
    """Render a single machine card inside the dashboard."""

    details_column, action_column = st.columns([4, 1.6])
    with details_column:
        render_machine_details(machine)

    with action_column:
        render_report_action(machine)


def render_report_action(machine: dict[str, Any]) -> None:
    """Render the quick action button for a busy machine."""

    if machine["inferred_status"] != "busy":
        return

    st.button(
        "Report as free",
        key=f"report-free-{machine['id']}",
        help="Report this machine as free.",
        use_container_width=True,
        on_click=queue_report_as_free,
        args=(machine["id"],),
    )
