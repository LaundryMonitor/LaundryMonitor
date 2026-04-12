def resolve_form_feedback(
    *,
    submit_message: str | None,
    submit_error: str | None,
    form_submit_message: str | None,
    form_submit_error: str | None,
) -> tuple[str | None, str | None]:
    """Prefer form feedback when the form was submitted."""

    if form_submit_message is None and form_submit_error is None:
        return submit_message, submit_error

    return form_submit_message, form_submit_error
