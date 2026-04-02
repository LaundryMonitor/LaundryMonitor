from frontend.api_client import LaundryAPIClient
from frontend.page.card_action import handle_card_action
from frontend.page.feedback import resolve_form_feedback
from frontend.page.flash import pop_flash_messages
from frontend.page.form_action import handle_form_action
from frontend.page.layout import (
    render_dashboard,
    render_feedback,
    render_load_error,
    render_page_header,
)
from frontend.page.state import load_page_state


def main() -> None:
    """Render the main Streamlit page and machine dashboard."""

    backend_url, refresh_requested = render_page_header()
    flash_success, flash_error = pop_flash_messages()
    client = LaundryAPIClient(backend_url)

    machines, load_error = load_page_state(client, refresh_requested=refresh_requested)
    submit_message, submit_error, machines = handle_card_action(
        client,
        machines=machines,
        load_error=load_error,
    )
    render_load_error(load_error)

    form_submit_message, form_submit_error, machines = handle_form_action(client, machines=machines)
    submit_message, submit_error = resolve_form_feedback(
        submit_message=submit_message,
        submit_error=submit_error,
        form_submit_message=form_submit_message,
        form_submit_error=form_submit_error,
    )
    render_feedback(
        flash_success=flash_success,
        flash_error=flash_error,
        submit_message=submit_message,
        submit_error=submit_error,
    )
    render_dashboard(machines, load_error)
