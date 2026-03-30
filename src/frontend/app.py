from __future__ import annotations

from datetime import datetime
from typing import Any

import streamlit as st

from frontend.api_client import (
    BackendResponseError,
    BackendUnavailableError,
    LaundryAPIClient,
    build_report_payload,
)
from frontend.config import BACKEND_URL_ENV_VAR, get_backend_base_url


STATUS_STYLES = {
    "free": ("Free", "#2e7d32"),
    "busy": ("Busy", "#c62828"),
    "probably_free": ("Probably Free", "#f9a825"),
    "unavailable": ("Unavailable", "#6b7280"),
}


def main() -> None:
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
    machines, load_error = _load_machines(client)

    if load_error:
        st.error(load_error)
    submit_message, submit_error, machines = _render_report_form(client, machines)

    if submit_message:
        st.success(submit_message)
    if submit_error:
        st.error(submit_error)

    if load_error:
        st.info("Machine dashboard is unavailable until backend data can be loaded.")
        return

    _render_machine_grid(machines)


def _load_machines(client: LaundryAPIClient) -> tuple[list[dict[str, Any]], str | None]:
    try:
        machines = client.get_machines()
    except (BackendUnavailableError, BackendResponseError) as exc:
        return [], str(exc)
    return machines, None


def _render_report_form(
    client: LaundryAPIClient,
    machines: list[dict[str, Any]],
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    st.subheader("Submit Report")

    if not machines:
        st.info("No machines available for reporting yet.")
        return None, None, machines

    machine_options = {
        f"{machine['name']} ({machine['type']})": machine["id"] for machine in machines
    }

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

    if not submitted:
        return None, None, machines

    machine_id = machine_options[selected_machine_label]
    try:
        payload = build_report_payload(
            machine_id=machine_id,
            status=status,
            time_remaining_text=time_remaining_text,
            reporter_name_text=reporter_name_text,
        )
        response_data = client.submit_report(payload)
    except ValueError as exc:
        return None, str(exc), machines
    except (BackendUnavailableError, BackendResponseError) as exc:
        return None, str(exc), machines

    try:
        refreshed_machines = client.get_machines()
    except (BackendUnavailableError, BackendResponseError) as exc:
        return (
            f"Report #{response_data['id']} submitted.",
            f"Report was submitted, but machine refresh failed: {exc}",
            machines,
        )

    return f"Report #{response_data['id']} submitted.", None, refreshed_machines


def _render_machine_grid(machines: list[dict[str, Any]]) -> None:
    st.subheader("Machine Dashboard")

    if not machines:
        st.info("No machines found. Run seed script and refresh.")
        return

    columns = st.columns(2)
    for index, machine in enumerate(machines):
        with columns[index % 2]:
            with _card_container():
                _render_machine_card(machine)


def _render_machine_card(machine: dict[str, Any]) -> None:
    st.markdown(f"**{machine['name']}**")
    st.caption(f"Type: {machine['type']}")
    _render_status_badge(machine["inferred_status"])

    has_reports = bool(machine.get("has_reports"))
    latest_report_at = machine.get("latest_report_at")
    if has_reports and latest_report_at:
        st.caption(f"Latest report: {_format_timestamp(latest_report_at)}")
    elif has_reports:
        st.caption("Latest report: available")
    else:
        st.caption("No reports yet")


def _render_status_badge(status: str) -> None:
    label, color = STATUS_STYLES.get(status, ("Unknown", "#6b7280"))
    st.markdown(
        (
            "<span style='display:inline-block;padding:0.2rem 0.7rem;"
            "border-radius:999px;color:white;font-size:0.85rem;"
            f"background:{color};'>{label}</span>"
        ),
        unsafe_allow_html=True,
    )


def _format_timestamp(raw_timestamp: str) -> str:
    normalized = raw_timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return raw_timestamp
    return parsed.strftime("%Y-%m-%d %H:%M")


def _card_container():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


if __name__ == "__main__":
    main()
