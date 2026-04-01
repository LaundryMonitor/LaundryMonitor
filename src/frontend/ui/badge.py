import streamlit as st


STATUS_STYLES = {
    "free": ("Free", "#2e7d32"),
    "busy": ("Busy", "#c62828"),
    "probably_free": ("Probably Free", "#f9a825"),
    "unavailable": ("Unavailable", "#6b7280"),
}


def render_status_badge(status: str) -> None:
    """Render a colored badge for one machine status."""

    label, color = STATUS_STYLES.get(status, ("Unknown", "#6b7280"))
    st.markdown(
        (
            "<span style='display:inline-block;padding:0.2rem 0.7rem;"
            "border-radius:999px;color:white;font-size:0.85rem;"
            f"background:{color};'>{label}</span>"
        ),
        unsafe_allow_html=True,
    )
