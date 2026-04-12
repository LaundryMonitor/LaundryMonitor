from typing import Any

import streamlit as st

from frontend.api_client import LaundryAPIClient
from frontend.page.state import store_page_state
from frontend.report_form.submission import submit_free_report
from frontend.ui.card import REPORT_AS_FREE_KEY


def handle_card_action(
    client: LaundryAPIClient,
    *,
    machines: list[dict[str, Any]],
    load_error: str | None,
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    """Handle a queued report-as-free action from a machine card."""

    if load_error:
        return None, None, machines

    machine_id = st.session_state.pop(REPORT_AS_FREE_KEY, None)
    if machine_id is None:
        return None, None, machines

    submit_message, submit_error, machines = submit_free_report(
        client,
        machine_id=machine_id,
        machines=machines,
    )
    store_page_state(machines)
    return submit_message, submit_error, machines
