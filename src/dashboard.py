from __future__ import annotations

from datetime import date
import time

import pandas as pd
import streamlit as st

from api_client import get_api_location_by_name, get_api_locations

from formatting import (
    format_change_for_display,
    format_date_for_display,
    format_duration_for_display,
    format_time_for_display,
)

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
            st.markdown(
                f"""
                <div class="daylight-result-card">
                    ✓ {success_message}
                </div>
                """,
                unsafe_allow_html=True,
           )

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
    """Viser siste måling som fem tydelige nøkkeltall."""

    st.subheader(
        f"Siste måling – {latest_measurement.location_name}"
    )

    st.caption(
        "Sist oppdatert "
        f"{format_date_for_display(latest_measurement.date)}"
    )

    metric_columns = st.columns(5, gap="small")

    # En felles liste holder kortenes struktur konsistent.
    metrics = [
        (
            "Dagslengde",
            format_duration_for_display(
                latest_measurement.day_length
            ),
        ),
        (
            "Soloppgang",
            format_time_for_display(
                latest_measurement.sunrise
            ),
        ),
        (
            "Solnedgang",
            format_time_for_display(
                latest_measurement.sunset
            ),
        ),
        (
            "Endring siden sist",
            format_change_for_display(
                latest_measurement.daily_increase
            ),
        ),
        (
            "Total endring",
            format_change_for_display(
                latest_measurement.total_increase
            ),
        ),
    ]

    for column, (label, value) in zip(
        metric_columns,
        metrics,
        strict=True,
    ):
        with column:
            # Containeren gir hvert nøkkeltall et eget visuelt kort.
            with st.container(border=True):
                st.metric(
                    label=label,
                    value=value,
                )


def render_charts(
    measurements_dataframe: pd.DataFrame,
) -> None:
    """Viser dagslengde og daglig endring som separate grafkort."""

    st.divider()
    st.subheader("Utvikling i dagslys")

    with st.container(border=True):
        st.markdown("#### Dagslengde")
        st.caption(
            "Utviklingen i antall timer dagslys gjennom perioden."
        )

        st.line_chart(
            measurements_dataframe,
            x="date",
            y="Dagslengde (timer)",
            height=340,
            use_container_width=True,
        )

    with st.container(border=True):
        st.markdown("#### Endring siden sist")
        st.caption(
            "Forskjellen fra den forrige lagrede målingen."
        )

        st.bar_chart(
            measurements_dataframe,
            x="date",
            y="Endring siden sist (minutter)",
            height=320,
            use_container_width=True,
        )


def render_history_table(
    measurements_dataframe: pd.DataFrame,
) -> None:
    """Viser lagrede målinger med lesbare norske verdier."""

    st.divider()
    st.subheader("Historikk")

    # Vi formaterer en kopi slik at grafdataene forblir numeriske.
    display_dataframe = measurements_dataframe.copy()

    display_dataframe = display_dataframe.sort_values(
        "date",
        ascending=False,
    )

    # Datoen i DataFrame-en er en pandas Timestamp.
    display_dataframe["date"] = display_dataframe["date"].map(
        lambda value: format_date_for_display(
            value.date().isoformat()
        )
    )

    display_dataframe["day_length"] = (
        display_dataframe["day_length"].map(
            format_duration_for_display
        )
    )

    display_dataframe["sunrise"] = (
        display_dataframe["sunrise"].map(
            format_time_for_display
        )
    )

    display_dataframe["sunset"] = (
        display_dataframe["sunset"].map(
            format_time_for_display
        )
    )

    display_dataframe["daily_increase"] = (
        display_dataframe["daily_increase"].map(
            format_change_for_display
        )
    )

    display_dataframe["total_increase"] = (
        display_dataframe["total_increase"].map(
            format_change_for_display
        )
    )

    # Bare kolonnene som er relevante for brukeren vises.
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

    # Rammen skiller historikken visuelt fra resten av dashboardet.
    with st.container(border=True):
        st.dataframe(
            display_dataframe,
            width="stretch",
            hide_index=True,
            height=420,
        )


def apply_custom_styles() -> None:
    """Tilpasser sidepanelet og bekreftelsesmeldingen."""

    st.markdown(
        """
        <style>
        /* Overskriften "Kontroller" */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            color: #17324D !important;
        }

        /* Etiketten "Sted" over dropdownen */
        [data-testid="stSidebar"] label p {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #17324D !important;
        }

        /* Forklaringsteksten under dropdownen */
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            line-height: 1.45 !important;
            color: #17324D !important;
        }

        /* Dropdownen for valg av sted */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #EAF6FF !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            color: #111827 !important;
            min-height: 44px !important;
        }

        /* Teksten inne i dropdownen */
        [data-testid="stSidebar"] div[data-baseweb="select"] span {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* Knappen "Hent dagens data" */
        [data-testid="stSidebar"] [data-testid="stButton"] > button {
            width: 100%;
            min-height: 44px;
            background-color: #EAF6FF !important;
            color: #111827 !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        /* Teksten inne i knappen */
        [data-testid="stSidebar"] [data-testid="stButton"] button p {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* Hover-effekt på knappen */
        [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
            background-color: #D8EEFA !important;
            border-color: #3689B8 !important;
            color: #111827 !important;
        }

        /* Bekreftelsesmeldingen etter lagring */
        .daylight-result-card {
            background-color: #EAF6FF !important;
            color: #111827 !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            padding: 12px 14px !important;
            margin: 10px 0 12px 0 !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            line-height: 1.45 !important;
        }

        .daylight-result-card span,
        .daylight-result-card strong {
            color: #111827 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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