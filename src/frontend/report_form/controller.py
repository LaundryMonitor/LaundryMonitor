from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import LaundryAPIClient
from frontend.report_form.fields import collect_report_fields
from frontend.report_form.submission import submit_report_form


def build_machine_options(machines: list[dict[str, Any]]) -> dict[str, int]:
    """Map human-readable machine labels to machine identifiers."""

    # Keep the form labels readable while preserving the machine ID lookup.
    return {
        f"{machine['name']} ({machine['type']})": machine["id"]
        for machine in machines
    }


def render_report_form(
    client: LaundryAPIClient,
    machines: list[dict[str, Any]],
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    """Render and process the Streamlit machine report form."""

    # Show the form header and handle the empty-state branch early.
    st.subheader("Submit Report")
    if not machines:
        st.info("No machines available for reporting yet.")
        return None, None, machines

    # Collect raw user inputs from the Streamlit widgets.
    machine_options = build_machine_options(machines)
    submitted, machine_label, status, time_remaining_text, reporter_name_text = (
        collect_report_fields(machine_options)
    )
    if not submitted:
        return None, None, machines

    # Submit the payload and return the refreshed machine list.
    return submit_report_form(
        client,
        machine_id=machine_options[machine_label],
        status=status,
        time_remaining_text=time_remaining_text,
        reporter_name_text=reporter_name_text,
        machines=machines,
    )
