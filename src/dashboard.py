from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from api_client import get_api_location_by_name, get_api_locations
from formatting import format_time_for_display
from measurement_service import fetch_and_save_measurement
from sqlite_storage import load_measurements


def load_dashboard_data() -> tuple[list, pd.DataFrame]:
    """Load saved measurements and convert them to a DataFrame for dashboard use."""

    # Leser alle lagrede målinger fra SQLite, som er hovedlagringen for dashboardet.
    measurements = load_measurements()

    if not measurements:
        return measurements, pd.DataFrame()

    # Gjør DaylightMeasurement-objektene om til dictionaries,
    # slik at pandas og Streamlit kan bruke dem.
    measurement_records = [measurement.to_dict() for measurement in measurements]
    measurements_dataframe = pd.DataFrame(measurement_records)

    # Konverterer dato fra tekst til datetime for riktig sortering og plotting.
    measurements_dataframe["date"] = pd.to_datetime(measurements_dataframe["date"])

    # Konverterer HH:MM:SS-strenger til tallverdier for grafer.
    measurements_dataframe["Day length (hours)"] = (
        pd.to_timedelta(measurements_dataframe["day_length"]).dt.total_seconds() / 3600
    )
    measurements_dataframe["Daily increase (minutes)"] = (
        pd.to_timedelta(measurements_dataframe["daily_increase"]).dt.total_seconds() / 60
    )

    return measurements, measurements_dataframe


def render_location_filter() -> str:
    """Render a location selector and return the selected location."""

    available_locations = sorted(get_api_locations().keys())

    selected_location = st.selectbox(
        "Selected location",
        options=available_locations,
    )

    return selected_location


def render_fetch_daylight_button(selected_location: str) -> None:
    """Render a button for fetching today's daylight data from MET Sunrise API."""

    st.divider()
    st.subheader("Update daylight data")
    st.write("Fetch today's sunrise and sunset from MET Sunrise API and save it to SQLite.")

    if st.button("Fetch today's daylight data"):
        location = get_api_location_by_name(selected_location)
        measurement = fetch_and_save_measurement(location, date.today())

        st.success(
            f"Saved daylight measurement for {measurement.location_name} "
            f"on {measurement.date}."
        )

        st.rerun()


def render_latest_metrics(latest_measurement) -> None:
    """Render metric cards for the latest saved daylight measurement."""

    st.subheader(f"Latest measurement — {latest_measurement.location_name}")
    st.caption(latest_measurement.date)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Day length", latest_measurement.day_length)

    with col2:
        st.metric("Sunrise", format_time_for_display(latest_measurement.sunrise))

    with col3:
        st.metric("Sunset", format_time_for_display(latest_measurement.sunset))

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Daily increase", latest_measurement.daily_increase)

    with col5:
        st.metric("Total increase", latest_measurement.total_increase)


def render_charts(measurements_dataframe: pd.DataFrame) -> None:
    """Render dashboard charts for daylight development."""

    st.divider()
    st.subheader("Light development per day")
    st.write("Day length measured in hours.")

    st.line_chart(
        measurements_dataframe,
        x="date",
        y="Day length (hours)",
    )

    st.write("Daily increase measured in minutes.")

    st.bar_chart(
        measurements_dataframe,
        x="date",
        y="Daily increase (minutes)",
    )


def render_history_table(measurements_dataframe: pd.DataFrame) -> None:
    """Render the saved measurements as a table."""

    st.divider()
    st.subheader("Lagrede målinger")

    # Lager en egen DataFrame for visningen, slik at formatering her ikke endrer grafdataene.
    display_dataframe = measurements_dataframe.copy()
    display_dataframe = display_dataframe.sort_values("date", ascending=False)

    # Viser bare datoen, uten klokkeslettet pandas legger til.
    display_dataframe["date"] = display_dataframe["date"].dt.date

    # Viser klokkeslett mer lesbart i tabellen.
    display_dataframe["sunrise"] = display_dataframe["sunrise"].map(format_time_for_display)
    display_dataframe["sunset"] = display_dataframe["sunset"].map(format_time_for_display)

    visible_columns = [
        "date",
        "location_name",
        "day_length",
        "sunrise",
        "sunset",
        "daily_increase",
        "total_increase",
    ]

    display_dataframe = display_dataframe[visible_columns]

    display_dataframe = display_dataframe.rename(
        columns={
            "date": "Date",
            "location_name": "Location",
            "day_length": "Day length",
            "sunrise": "Sunrise",
            "sunset": "Sunset",
            "daily_increase": "Daily increase",
            "total_increase": "Total increase",
        }
    )

    st.dataframe(
        display_dataframe,
        use_container_width=True,
        hide_index=True,
        height=400,
    )


def main() -> None:
    """Run the Streamlit dashboard."""

    st.set_page_config(
        page_title="Daylight Dashboard",
        page_icon="☀️",
        layout="wide",
    )

    st.title("Daylight Dashboard")
    st.write("A dashboard for daylight and seasonal development.")

    measurements, measurements_dataframe = load_dashboard_data()

    if not measurements:
        st.warning(
            "No SQLite measurements found. "
            "Run `python -m src.main --save-sqlite --location Grua` first."
        )
        return

    st.caption(f"Loaded {len(measurements)} measurements")

    selected_location = render_location_filter()

    render_fetch_daylight_button(selected_location)

    filtered_measurements = [
        measurement
        for measurement in measurements
        if measurement.location_name == selected_location
    ]
    
    if not filtered_measurements:
        st.info(
            f"No measurements found for {selected_location}. "
            "Fetch today's daylight data to start tracking this location."
        )
        return

    filtered_measurements_dataframe = measurements_dataframe[
        measurements_dataframe["location_name"] == selected_location
    ].copy()

    latest_measurement = filtered_measurements[-1]

    render_latest_metrics(latest_measurement)
    render_charts(filtered_measurements_dataframe)
    render_history_table(filtered_measurements_dataframe)


if __name__ == "__main__":
    main()