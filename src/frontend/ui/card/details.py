from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui.badge import render_status_badge
from frontend.ui.formatting import format_timestamp


def render_machine_details(machine: dict[str, Any]) -> None:
    """Render the text details shown on a machine card."""

    st.markdown(f"**{machine['name']}**")
    st.caption(f"Type: {machine['type']}")

    inferred_status = machine["inferred_status"]
    render_status_badge(inferred_status)
    render_latest_report(machine)


def render_latest_report(machine: dict[str, Any]) -> None:
    """Render the latest report label for a machine card."""

    has_reports = bool(machine.get("has_reports"))
    latest_report_at = machine.get("latest_report_at")
    if has_reports and latest_report_at:
        st.caption(f"Latest report: {format_timestamp(latest_report_at)}")
        return

    if has_reports:
        st.caption("Latest report: available")
        return

    st.caption("No reports yet")
