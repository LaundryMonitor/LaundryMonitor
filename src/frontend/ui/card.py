from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui.badge import render_status_badge
from frontend.ui.formatting import format_timestamp


def render_machine_card(machine: dict[str, Any]) -> None:
    """Render a single machine card inside the dashboard."""

    st.markdown(f"**{machine['name']}**")
    st.caption(f"Type: {machine['type']}")
    render_status_badge(machine["inferred_status"])

    has_reports = bool(machine.get("has_reports"))
    latest_report_at = machine.get("latest_report_at")
    if has_reports and latest_report_at:
        st.caption(f"Latest report: {format_timestamp(latest_report_at)}")
    elif has_reports:
        st.caption("Latest report: available")
    else:
        st.caption("No reports yet")
