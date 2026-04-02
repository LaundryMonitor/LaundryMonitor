from typing import Any

from frontend.api_client import LaundryAPIClient
from frontend.page.cache import store_page_state
from frontend.report_form import render_report_form


def handle_form_action(
    client: LaundryAPIClient,
    *,
    machines: list[dict[str, Any]],
) -> tuple[str | None, str | None, list[dict[str, Any]]]:
    """Handle the main report form submission."""

    submit_message, submit_error, machines = render_report_form(client, machines)
    if submit_message is None and submit_error is None:
        return None, None, machines

    store_page_state(machines)
    return submit_message, submit_error, machines
