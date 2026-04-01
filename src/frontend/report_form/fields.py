from __future__ import annotations

import streamlit as st


def collect_report_fields(
    machine_options: dict[str, int],
) -> tuple[bool, str, str, str, str]:
    """Collect report form inputs from Streamlit widgets."""

    with st.form("report_form", clear_on_submit=True):
        selected_machine_label = st.selectbox("Machine", options=list(machine_options))
        status = st.selectbox("Status", options=["busy", "free", "unavailable"])
        time_remaining_text = st.text_input(
            "Time remaining (minutes, optional)",
            value="",
            disabled=status != "busy",
            help="Only used for busy status.",
        )
        reporter_name_text = st.text_input("Reporter name (optional)", value="")
        submitted = st.form_submit_button("Submit Report")

    return (
        submitted,
        selected_machine_label,
        status,
        time_remaining_text,
        reporter_name_text,
    )
