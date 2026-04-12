from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.ui.card import render_machine_card
from frontend.ui.formatting import card_container


def render_machine_grid(machines: list[dict[str, Any]]) -> None:
    """Render the machine dashboard as a two-column grid."""

    st.subheader("Machine Dashboard")
    if not machines:
        st.info("No machines found. Run seed script and refresh.")
        return

    columns = st.columns(2)
    for index, machine in enumerate(machines):
        with columns[index % 2]:
            with card_container():
                render_machine_card(machine)
