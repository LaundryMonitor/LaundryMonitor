from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui.badge import render_status_badge
from frontend.ui.formatting import format_timestamp


REPORT_AS_FREE_KEY = "report_as_free_machine_id"


def queue_report_as_free(machine_id: int) -> None:
    """Queue a free report action from the machine card."""

    st.session_state[REPORT_AS_FREE_KEY] = machine_id


def render_machine_card(machine: dict[str, Any]) -> None:
    """Render a single machine card inside the dashboard."""

    details_column, action_column = st.columns([4, 1.6])

    with details_column:
        st.markdown(f"**{machine['name']}**")
        st.caption(f"Type: {machine['type']}")

        inferred_status = machine["inferred_status"]
        render_status_badge(inferred_status)

        has_reports = bool(machine.get("has_reports"))
        latest_report_at = machine.get("latest_report_at")
        if has_reports and latest_report_at:
            st.caption(f"Latest report: {format_timestamp(latest_report_at)}")
        elif has_reports:
            st.caption("Latest report: available")
        else:
            st.caption("No reports yet")

    with action_column:
        if machine["inferred_status"] == "busy":
            st.button(
                "Report as free",
                key=f"report-free-{machine['id']}",
                help="Report this machine as free.",
                use_container_width=True,
                on_click=queue_report_as_free,
                args=(machine["id"],),
            )
