from __future__ import annotations

import streamlit as st


FORM_MACHINE_KEY = "report_form_machine"
FORM_STATUS_KEY = "report_form_status"
FORM_TIME_REMAINING_KEY = "report_form_time_remaining"
FORM_REPORTER_KEY = "report_form_reporter"
FORM_RESET_KEY = "report_form_reset_requested"
DEFAULT_REPORT_STATUS = "busy"
REPORT_STATUS_OPTIONS = ["busy", "free", "unavailable"]


def apply_report_form_reset() -> None:
    """Apply a pending reset before rendering form widgets."""

    # Apply reset only when the previous submission requested it.
    if not st.session_state.pop(FORM_RESET_KEY, False):
        return

    # Restore form fields to their default values.
    st.session_state[FORM_STATUS_KEY] = DEFAULT_REPORT_STATUS
    st.session_state[FORM_TIME_REMAINING_KEY] = ""
    st.session_state[FORM_REPORTER_KEY] = ""


def initialize_report_form_state(machine_options: dict[str, int]) -> None:
    """Initialize default state for the report form widgets."""

    apply_report_form_reset()

    # Ensure the selected machine always points to an available option.
    default_machine_label = next(iter(machine_options))
    selected_machine_label = st.session_state.get(FORM_MACHINE_KEY)
    if selected_machine_label not in machine_options:
        st.session_state[FORM_MACHINE_KEY] = default_machine_label

    # Keep widget state aligned with supported report status values.
    if st.session_state.get(FORM_STATUS_KEY) not in REPORT_STATUS_OPTIONS:
        st.session_state[FORM_STATUS_KEY] = DEFAULT_REPORT_STATUS

    # Initialize optional text fields on first render.
    st.session_state.setdefault(FORM_TIME_REMAINING_KEY, "")
    st.session_state.setdefault(FORM_REPORTER_KEY, "")


def reset_report_form_state() -> None:
    """Reset report form fields after a successful submission."""

    st.session_state[FORM_RESET_KEY] = True


def collect_report_fields(
    machine_options: dict[str, int],
) -> tuple[bool, str, str, str, str]:
    """Collect report form inputs from Streamlit widgets."""

    # Prepare stable widget state before rendering the form controls.
    initialize_report_form_state(machine_options)

    # Render machine and status selectors first.
    selected_machine_label = st.selectbox(
        "Machine",
        options=list(machine_options),
        key=FORM_MACHINE_KEY,
    )
    status = st.radio(
        "Status",
        options=REPORT_STATUS_OPTIONS,
        horizontal=True,
        key=FORM_STATUS_KEY,
    )

    # Show remaining time only for busy reports.
    if status == "busy":
        time_remaining_text = st.text_input(
            "Time remaining (minutes, optional)",
            help="Only used for busy status.",
            key=FORM_TIME_REMAINING_KEY,
        )
    else:
        time_remaining_text = ""

    # Render optional metadata and the submit action last.
    reporter_name_text = st.text_input(
        "Reporter name (optional)",
        key=FORM_REPORTER_KEY,
    )
    submitted = st.button("Submit Report")

    return (
        submitted,
        selected_machine_label,
        status,
        time_remaining_text,
        reporter_name_text,
    )
