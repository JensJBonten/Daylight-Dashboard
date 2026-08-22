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
from measurement import DaylightMeasurement
from sqlite_storage import load_measurements


def load_dashboard_data() -> tuple[list[DaylightMeasurement], pd.DataFrame]:
    """Laster lagrede målinger og gjør dem klare for dashboardet."""

    measurements = load_measurements()

    if not measurements:
        return measurements, pd.DataFrame()

    # Pandas og Streamlit arbeider enklere med dictionaries enn modellobjekter.
    measurement_records = [
        measurement.to_dict()
        for measurement in measurements
    ]
    measurements_dataframe = pd.DataFrame(measurement_records)

    # Konverteringene gir riktig sortering og numeriske akser i grafene.
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
    """Starter Streamlit-dashboardet."""

    st.set_page_config(
        page_title="Dagslysdashboard",
        page_icon="☀️",
        layout="wide",
    )

    apply_custom_styles()

    st.title("Dagslysdashboard")
    st.write(
        "Følg utviklingen i dagslengde, soloppgang og solnedgang "
        "for utvalgte steder i Norge."
    )

    selected_location = render_sidebar_controls()

    render_season_overview(selected_location)

    measurements, measurements_dataframe = load_dashboard_data()

    if not measurements:
        st.info(
            "Ingen målinger er lagret ennå. Velg et sted i sidepanelet "
            "og sjekk inn for å opprette den første målingen."
        )
        return

    st.caption(f"{len(measurements)} lagrede målinger totalt")

    filtered_measurements = [
        measurement
        for measurement in measurements
        if measurement.location_name == selected_location
    ]

    if not filtered_measurements:
        st.info(
            f"Det finnes ingen lagrede målinger for {selected_location}. "
            "Bruk knappen i sidepanelet for å sjekke inn."
        )
        return

    filtered_measurements_dataframe = measurements_dataframe[
        measurements_dataframe["location_name"] == selected_location
    ].copy()

    latest_measurement = filtered_measurements[-1]

    render_latest_metrics(latest_measurement)

    render_reference_chart(
        selected_location,
        filtered_measurements_dataframe,
    )

    render_charts(filtered_measurements_dataframe)
    render_history_table(filtered_measurements_dataframe)


if __name__ == "__main__":
    main()
