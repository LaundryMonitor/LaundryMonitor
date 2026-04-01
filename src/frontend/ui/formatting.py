from __future__ import annotations

from datetime import datetime

import streamlit as st


def format_timestamp(raw_timestamp: str) -> str:
    """Format an ISO timestamp string for dashboard display."""

    normalized = raw_timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return raw_timestamp
    return parsed.strftime("%Y-%m-%d %H:%M")


def card_container():
    """Return a bordered container when supported by Streamlit."""

    try:
        return st.container(border=True)
    except TypeError:
        return st.container()
