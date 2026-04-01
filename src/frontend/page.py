import streamlit as st

from frontend.api_client import LaundryAPIClient
from frontend.config import BACKEND_URL_ENV_VAR, get_backend_base_url
from frontend.loader import load_machines
from frontend.report_form import render_report_form
from frontend.ui import render_machine_grid


def main() -> None:
    """Render the main Streamlit page and machine dashboard."""

    st.set_page_config(page_title="Laundry Monitor", layout="wide")
    st.title("Laundry Monitor")

    backend_url = get_backend_base_url()
    st.caption(
        f"Backend URL: `{backend_url}` "
        f"(override with `{BACKEND_URL_ENV_VAR}` environment variable)."
    )

    if st.button("Refresh"):
        st.rerun()

    client = LaundryAPIClient(backend_url)
    machines, load_error = load_machines(client)

    if load_error:
        st.error(load_error)
    submit_message, submit_error, machines = render_report_form(client, machines)

    if submit_message:
        st.success(submit_message)
    if submit_error:
        st.error(submit_error)

    if load_error:
        st.info("Machine dashboard is unavailable until backend data can be loaded.")
        return

    render_machine_grid(machines)
