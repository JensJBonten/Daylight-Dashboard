from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from plotting import (
    build_reference_daylight_chart,
)
from reference_data import (
    ReferenceDataError,
    load_reference_data,
)


def render_reference_chart(
    selected_location: str,
    measurements_dataframe: pd.DataFrame,
    accent_color: str,
) -> None:
    """Render MET reference data and saved measurements in one chart."""

    current_year = date.today().year

    try:
        reference_data = (
            load_reference_data(
                selected_location,
                year=current_year,
            )
        )

    except ReferenceDataError:
        st.info(
            "Referansegrafen er ikke tilgjengelig akkurat nå."
        )
        return

    if reference_data.empty:
        st.info(
            "Det finnes ikke referansedata for "
            f"{selected_location} ennå."
        )
        return

    if measurements_dataframe.empty:
        personal_measurements = (
            pd.DataFrame(
                columns=[
                    "date",
                    "Dagslengde (timer)",
                ]
            )
        )

    else:
        personal_measurements = (
            measurements_dataframe[
                measurements_dataframe[
                    "date"
                ].dt.year
                == current_year
            ].copy()
        )

    reference_chart = (
        build_reference_daylight_chart(
            reference_data,
            personal_measurements,
            accent_color,
        )
    )

    st.divider()

    st.subheader(
        "Dagslys gjennom året"
    )

    st.caption(
        "Den svake linjen viser ukentlige MET-referanseverdier. "
        "De tydelige punktene viser dine egne lagrede målinger."
    )

    with st.container(
        border=True,
        key="reference_chart_card",
    ):
        st.altair_chart(
            reference_chart,
            use_container_width=True,
            theme=None,
        )