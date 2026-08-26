from __future__ import annotations

import pandas as pd
import streamlit as st

from formatting import (
    format_change_for_display,
    format_date_for_display,
    format_duration_for_display,
    format_time_for_display,
)


def render_history_table(
    measurements_dataframe: pd.DataFrame,
) -> None:
    """Render saved measurements in a clean dashboard table."""

    st.divider()
    st.subheader("Historikk")

    display_dataframe = measurements_dataframe.copy()

    measurement_count = len(
        display_dataframe
    )

    if display_dataframe.empty:
        st.caption(
            "Ingen lagrede målinger for valgt sted."
        )
        return

    selected_location = (
        display_dataframe[
            "location_name"
        ].iloc[0]
    )

    st.caption(
        f"{measurement_count} lagrede målinger "
        f"for {selected_location}. "
        "Nyeste måling vises øverst."
    )

    display_dataframe = (
        display_dataframe.sort_values(
            "date",
            ascending=False,
        )
    )

    display_dataframe["date"] = (
        display_dataframe["date"].map(
            lambda value: (
                format_date_for_display(
                    value.date().isoformat()
                )
            )
        )
    )

    display_dataframe["day_length"] = (
        display_dataframe[
            "day_length"
        ].map(
            format_duration_for_display
        )
    )

    display_dataframe["sunrise"] = (
        display_dataframe[
            "sunrise"
        ].map(
            format_time_for_display
        )
    )

    display_dataframe["sunset"] = (
        display_dataframe[
            "sunset"
        ].map(
            format_time_for_display
        )
    )

    display_dataframe["daily_increase"] = (
        display_dataframe[
            "daily_increase"
        ].map(
            format_change_for_display
        )
    )

    display_dataframe["total_increase"] = (
        display_dataframe[
            "total_increase"
        ].map(
            format_change_for_display
        )
    )

    visible_columns = [
        "date",
        "day_length",
        "sunrise",
        "sunset",
        "daily_increase",
        "total_increase",
    ]

    display_dataframe = (
        display_dataframe[
            visible_columns
        ]
    )

    display_dataframe = (
        display_dataframe.rename(
            columns={
                "date": "Dato",
                "day_length": "Dagslengde",
                "sunrise": "Soloppgang",
                "sunset": "Solnedgang",
                "daily_increase": (
                    "Endring siden sist"
                ),
                "total_increase": (
                    "Total endring"
                ),
            }
        )
    )

    with st.container(
        border=True,
        key="history_card",
    ):
        st.dataframe(
            display_dataframe,
            width="stretch",
            hide_index=True,
            height=420,
            column_config={
                "Dato": (
                    st.column_config.TextColumn(
                        "Dato",
                        width="small",
                    )
                ),
                "Dagslengde": (
                    st.column_config.TextColumn(
                        "Dagslengde",
                        width="small",
                    )
                ),
                "Soloppgang": (
                    st.column_config.TextColumn(
                        "Soloppgang",
                        width="small",
                    )
                ),
                "Solnedgang": (
                    st.column_config.TextColumn(
                        "Solnedgang",
                        width="small",
                    )
                ),
                "Endring siden sist": (
                    st.column_config.TextColumn(
                        "Endring siden sist",
                        width="medium",
                    )
                ),
                "Total endring": (
                    st.column_config.TextColumn(
                        "Total endring",
                        width="medium",
                    )
                ),
            },
        )

