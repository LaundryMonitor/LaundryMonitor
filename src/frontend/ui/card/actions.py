import streamlit as st


REPORT_AS_FREE_KEY = "report_as_free_machine_id"


def queue_report_as_free(machine_id: int) -> None:
    """Queue a free report action from the machine card."""

    st.session_state[REPORT_AS_FREE_KEY] = machine_id
