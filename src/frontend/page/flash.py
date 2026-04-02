import streamlit as st


FLASH_SUCCESS_KEY = "page_flash_success"
FLASH_ERROR_KEY = "page_flash_error"


def pop_flash_messages() -> tuple[str | None, str | None]:
    """Read and clear one-time feedback messages."""

    flash_success = st.session_state.pop(FLASH_SUCCESS_KEY, None)
    flash_error = st.session_state.pop(FLASH_ERROR_KEY, None)
    return flash_success, flash_error
