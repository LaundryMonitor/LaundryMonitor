import streamlit as st

from frontend.api_client import LaundryAPIClient
from frontend.config import BACKEND_URL_ENV_VAR, get_backend_base_url
from frontend.loader import load_machines
from frontend.report_form import render_report_form
from frontend.report_form.submission import submit_free_report
from frontend.ui.card import REPORT_AS_FREE_KEY
from frontend.ui import render_machine_grid


MACHINES_STATE_KEY = "page_machines"
LOAD_ERROR_STATE_KEY = "page_load_error"
FLASH_SUCCESS_KEY = "page_flash_success"
FLASH_ERROR_KEY = "page_flash_error"


def main() -> None:
    """Render the main Streamlit page and machine dashboard."""

    st.set_page_config(page_title="Laundry Monitor", layout="wide")
    st.title("Laundry Monitor")

    backend_url = get_backend_base_url()
    st.caption(
        f"Backend URL: `{backend_url}` "
        f"(override with `{BACKEND_URL_ENV_VAR}` environment variable)."
    )

    refresh_requested = st.button("Refresh")

    flash_success = st.session_state.pop(FLASH_SUCCESS_KEY, None)
    flash_error = st.session_state.pop(FLASH_ERROR_KEY, None)

    client = LaundryAPIClient(backend_url)
    if refresh_requested or MACHINES_STATE_KEY not in st.session_state:
        machines, load_error = load_machines(client)
        st.session_state[MACHINES_STATE_KEY] = machines
        st.session_state[LOAD_ERROR_STATE_KEY] = load_error
    else:
        machines = st.session_state[MACHINES_STATE_KEY]
        load_error = st.session_state[LOAD_ERROR_STATE_KEY]
    submit_message: str | None = None
    submit_error: str | None = None

    if not load_error:
        report_as_free_machine_id = st.session_state.pop(REPORT_AS_FREE_KEY, None)
    else:
        report_as_free_machine_id = None

    if report_as_free_machine_id is not None:
        submit_message, submit_error, machines = submit_free_report(
            client,
            machine_id=report_as_free_machine_id,
            machines=machines,
        )
        st.session_state[MACHINES_STATE_KEY] = machines
        st.session_state[LOAD_ERROR_STATE_KEY] = None

    if load_error:
        st.error(load_error)
    form_submit_message, form_submit_error, machines = render_report_form(client, machines)
    feedback_placeholder = st.empty()
    if form_submit_message is not None or form_submit_error is not None:
        submit_message = form_submit_message
        submit_error = form_submit_error
        st.session_state[MACHINES_STATE_KEY] = machines
        st.session_state[LOAD_ERROR_STATE_KEY] = None

    with feedback_placeholder.container():
        if flash_success:
            st.success(flash_success)
        if flash_error:
            st.error(flash_error)
        if submit_message:
            st.success(submit_message)
        if submit_error:
            st.error(submit_error)

    if load_error:
        st.info("Machine dashboard is unavailable until backend data can be loaded.")
        return

    render_machine_grid(machines)
