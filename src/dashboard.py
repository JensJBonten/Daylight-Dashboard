from __future__ import annotations

from datetime import date
import time

import pandas as pd
import streamlit as st

from api_client import get_api_location_by_name, get_api_locations
from formatting import format_time_for_display
from measurement import DaylightMeasurement
from measurement_service import (
    fetch_and_save_measurement, 
    DaylightServiceError,
)
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


def render_sidebar_controls() -> str:
    """Viser stedvalg og kontroll for å hente dagens MET-data."""

    available_locations = sorted(get_api_locations().keys())

    with st.sidebar:
        st.header("Kontroller")

        selected_location = st.selectbox(
            "Sted",
            options=available_locations,
        )

        st.caption(
            "Henter dagens soloppgang og solnedgang fra MET "
            "og lagrer målingen i SQLite."
        )
        
        # Melding lagres før rerun og vises en gang etter oppdateringen. 
        success_message = st.session_state.pop(
            "daylight_success_message",
             None,
        )
        
        if success_message:
            st.success(success_message)

        if st.button(
            "Hent dagens data",
            use_container_width=True,
        ):
            location = get_api_location_by_name(selected_location)
            
            try: 
                #legger til en liten spinner som snurrer i sidepanelet mens arbeidsflyten kjører, indikasjon på at det skjer noe. 
                with st.spinner("henter dagslysdata!"):
                    time.sleep(2) #lagt til time 2 for å sjekke om spinner fungerer.
                    measurement = fetch_and_save_measurement(
                        location,
                        date.today(),
                    )
            
            except DaylightServiceError:
                st.error(
                    "Kunne ikke hente eller lagre dagslysdataen."
                    "Kontroller nettforbindelsen og prøv igjen."
                )

            else:
                # Else-blokken kjøres bare dersom try-blokken lykkes.
                formatted_date = date.fromisoformat(
                    measurement.date
                ).strftime("%d.%m.%Y")

                st.session_state["daylight_success_message"] = (
                    f"Nice! Målingen for {measurement.location_name} "
                    f"den {formatted_date} ble lagret."
                )

                # Dashboardet kjøres på nytt slik at nye data vises umiddelbart.
                st.rerun()

    return selected_location


def render_latest_metrics(
    latest_measurement: DaylightMeasurement,
) -> None:
    """Viser nøkkeltall for siste lagrede måling."""

    st.subheader(f"Siste måling – {latest_measurement.location_name}")
    st.caption(latest_measurement.date)

    day_length_column, sunrise_column, sunset_column = st.columns(3)

    with day_length_column:
        st.metric(
            "Dagslengde",
            latest_measurement.day_length,
        )

    with sunrise_column:
        st.metric(
            "Soloppgang",
            format_time_for_display(latest_measurement.sunrise),
        )

    with sunset_column:
        st.metric(
            "Solnedgang",
            format_time_for_display(latest_measurement.sunset),
        )

    daily_increase_column, total_increase_column = st.columns(2)

    with daily_increase_column:
        st.metric(
            "Endring siden sist",
            latest_measurement.daily_increase,
        )

    with total_increase_column:
        st.metric(
            "Total endring",
            latest_measurement.total_increase,
        )


def render_charts(
    measurements_dataframe: pd.DataFrame,
) -> None:
    """Viser grafer for utviklingen i dagslys."""

    st.divider()
    st.subheader("Utvikling i dagslys")

    st.write("Dagslengde målt i timer.")

    st.line_chart(
        measurements_dataframe,
        x="date",
        y="Dagslengde (timer)",
    )

    st.write("Endring siden sist lagrede måling, målt i minutter.")

    st.bar_chart(
        measurements_dataframe,
        x="date",
        y="Endring siden sist (minutter)",
    )


def render_history_table(
    measurements_dataframe: pd.DataFrame,
) -> None:
    """Viser lagrede målinger i en historikktabell."""

    st.divider()
    st.subheader("Historikk")

    # Visningsformatering holdes separat fra dataene som brukes i grafene.
    display_dataframe = measurements_dataframe.copy()
    display_dataframe = display_dataframe.sort_values(
        "date",
        ascending=False,
    )

    display_dataframe["date"] = display_dataframe["date"].dt.date

    display_dataframe["sunrise"] = display_dataframe["sunrise"].map(
        format_time_for_display
    )
    display_dataframe["sunset"] = display_dataframe["sunset"].map(
        format_time_for_display
    )

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
            "date": "Dato",
            "location_name": "Sted",
            "day_length": "Dagslengde",
            "sunrise": "Soloppgang",
            "sunset": "Solnedgang",
            "daily_increase": "Endring siden sist",
            "total_increase": "Total endring",
        }
    )

    st.dataframe(
        display_dataframe,
        use_container_width=True,
        hide_index=True,
        height=400,
    )


def main() -> None:
    """Starter Streamlit-dashboardet."""

    st.set_page_config(
        page_title="Dagslysdashboard",
        page_icon="☀️",
        layout="wide",
    )

    st.title("Dagslysdashboard")
    st.write(
        "Følg utviklingen i dagslengde, soloppgang og solnedgang "
        "for utvalgte steder i Norge."
    )

    # Sidepanelet må vises før data kontrolleres, slik at en tom database
    # fortsatt kan hente og lagre sin første måling.
    selected_location = render_sidebar_controls()

    measurements, measurements_dataframe = load_dashboard_data()

    if not measurements:
        st.info(
            "Ingen målinger er lagret ennå. Velg et sted i sidepanelet "
            "og hent dagens data for å opprette den første målingen."
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
            "Bruk knappen i sidepanelet for å hente dagens data."
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