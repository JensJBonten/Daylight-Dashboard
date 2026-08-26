from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard_components import (
    render_charts,
    render_history_table,
    render_latest_metrics,
    render_reference_chart,
    render_season_overview,
    render_sidebar_controls,
)
from dashboard_styles import apply_custom_styles
from historical_seed import seed_historical_data
from measurement import DaylightMeasurement
from sqlite_storage import load_measurements


def load_dashboard_data() -> tuple[list[DaylightMeasurement], pd.DataFrame]:
    """Load saved measurements and prepare them for the dashboard."""

    measurements = load_measurements()

    if not measurements:
        return measurements, pd.DataFrame()

    measurement_records = [
        measurement.to_dict()
        for measurement in measurements
    ]
    measurements_dataframe = pd.DataFrame(measurement_records)

    measurements_dataframe["date"] = pd.to_datetime(
        measurements_dataframe["date"]
    )

    measurements_dataframe["Dagslengde (timer)"] = (
        pd.to_timedelta(
            measurements_dataframe["day_length"]
        ).dt.total_seconds()
        / 3600
    )

    measurements_dataframe["Endring siden sist (minutter)"] = (
        pd.to_timedelta(
            measurements_dataframe["daily_increase"]
        ).dt.total_seconds()
        / 60
    )

    return measurements, measurements_dataframe


def main() -> None:
    """Start the Streamlit dashboard."""

    st.set_page_config(
        page_title="Dagslysdashboard",
        page_icon="☀️",
        layout="wide",
    )

    apply_custom_styles()

    seed_historical_data()

    st.title("Dagslysdashboard")

    st.write(
        "Følg utviklingen i dagslengde, soloppgang og solnedgang "
        "for utvalgte steder i Norge."
    )

    selected_location = render_sidebar_controls()

    (
        season_theme,
        daylight_change_since_solstice,
    ) = render_season_overview(
        selected_location
    )

    measurements, measurements_dataframe = load_dashboard_data()

    if measurements_dataframe.empty:
        selected_measurements_dataframe = pd.DataFrame()
    else:
        selected_measurements_dataframe = measurements_dataframe[
            measurements_dataframe["location_name"]
            == selected_location
        ].copy()

    if not measurements:
        render_reference_chart(
            selected_location,
            selected_measurements_dataframe,
            season_theme.accent,
        )

        st.info(
            "Ingen egne målinger er lagret ennå. "
            "Bruk «Sjekk inn i dag» i sidepanelet "
            "for å registrere den første målingen."
        )
        return

    filtered_measurements = [
        measurement
        for measurement in measurements
        if measurement.location_name == selected_location
    ]

    if not filtered_measurements:
        render_reference_chart(
            selected_location,
            selected_measurements_dataframe,
            season_theme.accent,
        )

        st.info(
            f"Det finnes ingen egne målinger for "
            f"{selected_location} ennå. "
            "MET-referansekurven kan fortsatt "
            "brukes som sammenligning."
        )
        return

    latest_measurement = filtered_measurements[-1]

    render_latest_metrics(
        latest_measurement,
        filtered_measurements,
        daylight_change_since_solstice,
    )

    render_reference_chart(
        selected_location,
        selected_measurements_dataframe,
        season_theme.accent,
    )

    render_charts(
        selected_measurements_dataframe,
        season_theme.accent,
    )

    render_history_table(
        selected_measurements_dataframe,
        season_theme.background,
        season_theme.accent,
    )


if __name__ == "__main__":
    main()