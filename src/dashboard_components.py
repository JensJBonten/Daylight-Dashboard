from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from api_client import get_api_location_by_name, get_api_locations
from dashboard_styles import apply_season_sidebar_style
from formatting import (
    format_change_as_story,
    format_change_for_display,
    format_date_for_display,
    format_duration_for_display,
    format_time_for_display,
)
from measurement import DaylightMeasurement
from measurement_service import (
    DaylightServiceError,
    fetch_and_save_measurement,
)
from plotting import build_reference_daylight_chart
from reference_data import (
    ReferenceDataError,
    load_reference_data,
)
from seasonal import (
    SeasonTheme,
    calculate_change_since_solstice,
    format_hours_change_as_story,
    get_next_solstice,
    get_previous_solstice,
    get_season_theme,
)
from sqlite_storage import load_check_in_dates


def render_sidebar_controls() -> str:
    """Render location selection and today's check-in control."""

    available_locations = sorted(get_api_locations().keys())
    default_location_index = available_locations.index("Oslo")

    today = date.today()
    today_iso = today.isoformat()

    with st.sidebar:
        st.header("Kontroller")

        selected_location = st.selectbox(
            "Sted",
            options=available_locations,
            index=default_location_index,
        )

        check_in_dates = load_check_in_dates(selected_location)
        already_checked_in_today = today_iso in check_in_dates

        st.caption(
            "Henter dagens dagslysdata fra MET og registrerer "
            "dagens felles måling."
        )

        if check_in_dates:
            latest_check_in = max(check_in_dates)

            formatted_latest_check_in = date.fromisoformat(
                latest_check_in
            ).strftime("%d.%m.%Y")

            if already_checked_in_today:
                st.caption("✓ Dagens måling er allerede registrert.")
            else:
                st.caption(
                    f"Sist innsjekket: {formatted_latest_check_in}"
                )
        else:
            st.caption("Ingen innsjekkinger ennå.")

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

        button_label = (
            "Dagens måling registrert ✓"
            if already_checked_in_today
            else "Sjekk inn i dag"
        )

        if st.button(
            button_label,
            use_container_width=True,
            disabled=already_checked_in_today,
        ):
            location = get_api_location_by_name(selected_location)

            try:
                with st.spinner("Henter dagslysdata!"):
                    measurement = fetch_and_save_measurement(
                        location,
                        today,
                    )

            except DaylightServiceError:
                st.error(
                    "Kunne ikke hente eller lagre dagslysdataen. "
                    "Kontroller nettforbindelsen og prøv igjen."
                )

            else:
                formatted_date = date.fromisoformat(
                    measurement.date
                ).strftime("%d.%m.%Y")

                st.session_state["daylight_success_message"] = (
                    f"Innsjekking registrert for "
                    f"{measurement.location_name} "
                    f"{formatted_date}."
                )

                st.rerun()

    return selected_location


def render_season_overview(
    selected_location: str,
) -> tuple[SeasonTheme, float | None]:
    """Render the active season and return its theme and solstice change."""

    today = date.today()

    # Previewing a season changes only the visual theme.
    season_preview_dates = {
        "Automatisk – dagens dato": today,
        "❄️ Vinter": date(today.year, 1, 15),
        "🌱 Vår": date(today.year, 4, 15),
        "☀️ Sommer": date(today.year, 7, 15),
        "🍂 Høst": date(today.year, 9, 15),
        "🎃 Halloween": date(today.year, 10, 15),
        "🎅 Jul": date(today.year, 12, 15),
    }

    with st.sidebar.expander(
        "Forhåndsvis sesongtema"
    ):
        selected_preview = st.selectbox(
            "Forhåndsvis tema",
            options=list(
                season_preview_dates.keys()
            ),
        )

        st.caption(
            "Forhåndsvisningen endrer kun sesongtemaet."
        )

    theme_date = season_preview_dates[
        selected_preview
    ]

    season = get_season_theme(
        theme_date
    )

    month_names = {
        1: "Januar",
        2: "Februar",
        3: "Mars",
        4: "April",
        5: "Mai",
        6: "Juni",
        7: "Juli",
        8: "August",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }

    month_name = month_names[
        theme_date.month
    ]

    if season.name in (
        "Halloween",
        "Jul",
    ):
        season_heading = (
            f"{month_name} ({season.name})"
        )
    else:
        season_heading = month_name

    apply_season_sidebar_style(
        background_color=season.background,
        accent_color=season.accent,
    )

    # Solstice calculations always use the real date,
    # even when another visual theme is previewed.
    next_solstice = get_next_solstice(
        today
    )

    days_until_solstice = (
        next_solstice.date - today
    ).days

    formatted_next_solstice = (
        next_solstice.date.strftime(
            "%d.%m.%Y"
        )
    )

    daylight_change = None

    try:
        reference_data = load_reference_data(
            selected_location,
            year=today.year,
        )

        if not reference_data.empty:
            daylight_change = (
                calculate_change_since_solstice(
                    reference_data,
                    today,
                )
            )

    except ReferenceDataError:
        daylight_change = None

    season_card = f"""
<div style="
background-color: {season.background};
border: 1px solid {season.accent};
border-left: 6px solid {season.accent};
border-radius: 12px;
padding: 16px 20px;
margin: 18px 0 22px 0;
">
<div style="
font-size: 1.25rem;
font-weight: 800;
margin-bottom: 7px;
">
{season.icon} {season_heading}
</div>
<div style="
font-size: 0.95rem;
">
{next_solstice.icon} Neste: {next_solstice.name}
{formatted_next_solstice} · {days_until_solstice} dager igjen
</div>
</div>
"""

    st.markdown(
        season_card,
        unsafe_allow_html=True,
    )

    return season, daylight_change


def _toggle_change_metric_view(
    state_key: str,
) -> None:
    """Toggle between check-in and solstice change."""

    current_view = st.session_state.get(
        state_key,
        "check_in",
    )

    st.session_state[state_key] = (
        "solstice"
        if current_view == "check_in"
        else "check_in"
    )


def render_latest_metrics(
    latest_measurement: DaylightMeasurement,
    measurements_for_location: list[DaylightMeasurement],
    daylight_change_since_solstice: float | None,
) -> None:
    """Render four metrics with a toggleable daylight-change card."""

    st.subheader(
        f"Siste måling – {latest_measurement.location_name}"
    )

    st.caption(
        "Sist oppdatert "
        f"{format_date_for_display(latest_measurement.date)}"
    )

    check_in_dates = sorted(
        load_check_in_dates(
            latest_measurement.location_name
        )
    )

    measurements_by_date = {
        measurement.date: measurement
        for measurement in measurements_for_location
    }

    latest_check_in_measurement = None

    if check_in_dates:
        latest_check_in_measurement = (
            measurements_by_date.get(
                check_in_dates[-1]
            )
        )

    if (
        latest_check_in_measurement is not None
        and len(check_in_dates) >= 2
    ):
        manual_value = format_change_as_story(
            latest_check_in_measurement.daily_increase
        )

        manual_caption = (
            "Sammenlignet med "
            f"{format_date_for_display(check_in_dates[-2])}"
        )

    elif latest_check_in_measurement is not None:
        manual_value = "Første innsjekk"

        manual_caption = (
            "Registrert "
            f"{format_date_for_display(check_in_dates[-1])}"
        )

    else:
        manual_value = "Ingen innsjekk"
        manual_caption = "Bruk «Sjekk inn i dag»"

    previous_solstice = get_previous_solstice(
        date.today()
    )

    solstice_label = (
        f"Siden {previous_solstice.name.lower()}"
    )

    if daylight_change_since_solstice is None:
        solstice_value = "Ikke tilgjengelig"
        solstice_caption = "Mangler referansedata"
    else:
        solstice_value = format_hours_change_as_story(
            daylight_change_since_solstice
        )

        solstice_caption = (
            "Sammenlignet med "
            f"{previous_solstice.date.strftime('%d.%m.%Y')}"
        )

    state_key = (
        "change_metric_view_"
        f"{latest_measurement.location_name}"
    )

    if state_key not in st.session_state:
        st.session_state[state_key] = "check_in"

    change_view = st.session_state[state_key]

    if change_view == "solstice":
        change_label = solstice_label
        change_value = solstice_value
        change_caption = solstice_caption
        navigation_indicator = "○ ●"
        navigation_arrow = "←"
        navigation_help = (
            "Vis endring siden siste innsjekk"
        )
    else:
        change_label = "Siden siste innsjekk"
        change_value = manual_value
        change_caption = manual_caption
        navigation_indicator = "● ○"
        navigation_arrow = "→"
        navigation_help = (
            "Vis endring siden forrige solverv"
        )

    metric_columns = st.columns(
        4,
        gap="small",
        vertical_alignment="top",
        border=True,
    )

    fixed_metrics = [
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
    ]

    for column, (label, value) in zip(
        metric_columns[:3],
        fixed_metrics,
        strict=True,
    ):
        with column:
            st.metric(
                label=label,
                value=value,
            )

    with metric_columns[3], st.container(
        key="change_metric_card"
    ):
        st.metric(
            label=change_label,
            value=change_value,
        )

        navigation_columns = st.columns(
            [5, 1],
            gap="small",
        )

        with navigation_columns[0]:
            st.caption(
                f"{change_caption} "
                f"· {navigation_indicator}"
            )

        with navigation_columns[1]:
            st.button(
                navigation_arrow,
                key=(
                    "toggle_change_metric_"
                    f"{latest_measurement.location_name}"
                ),
                help=navigation_help,
                type="tertiary",
                use_container_width=True,
                on_click=_toggle_change_metric_view,
                args=(state_key,),
            )


def render_reference_chart(
    selected_location: str,
    measurements_dataframe: pd.DataFrame,
    accent_color: str,
) -> None:
    """Render MET reference data and saved measurements in one chart."""

    current_year = date.today().year

    try:
        reference_data = load_reference_data(
            selected_location,
            year=current_year,
        )

    except ReferenceDataError:
        st.info(
            "Referansegrafen er ikke tilgjengelig akkurat nå."
        )
        return

    if reference_data.empty:
        st.info(
            f"Det finnes ikke referansedata for "
            f"{selected_location} ennå."
        )
        return

    if measurements_dataframe.empty:
        personal_measurements = pd.DataFrame(
            columns=[
                "date",
                "Dagslengde (timer)",
            ]
        )

    else:
        personal_measurements = measurements_dataframe[
            measurements_dataframe["date"].dt.year
            == current_year
        ].copy()

    reference_chart = build_reference_daylight_chart(
        reference_data,
        personal_measurements,
        accent_color,
    )

    st.divider()
    st.subheader("Dagslys gjennom året")

    st.caption(
        "Den svake linjen viser ukentlige MET-referanseverdier. "
        "De tydelige punktene viser dine egne lagrede målinger."
    )

    with st.container(border=True):
        st.altair_chart(
            reference_chart,
            use_container_width=True,
        )


def render_charts(
    measurements_dataframe: pd.DataFrame,
    accent_color: str,
) -> None:
    """Render day length and daily change as separate chart cards."""

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
            color=accent_color,
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
            color=accent_color,
            height=320,
            use_container_width=True,
        )


def render_history_table(
    measurements_dataframe: pd.DataFrame,
    background_color: str,
    accent_color: str,
) -> None:
    """Render saved measurements with readable Norwegian values."""

    st.divider()
    st.subheader("Historikk")

    display_dataframe = measurements_dataframe.copy()

    display_dataframe = display_dataframe.sort_values(
        "date",
        ascending=False,
    )

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

    # Apply seasonal color only to the header so the data remains neutral.
    styled_dataframe = display_dataframe.style.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    (
                        "background-color",
                        background_color,
                    ),
                    (
                        "color",
                        "#17324D",
                    ),
                    (
                        "border-bottom",
                        f"2px solid {accent_color}",
                    ),
                ],
            }
        ]
    )

    with st.container(border=True):
        st.dataframe(
            styled_dataframe,
            width="stretch",
            hide_index=True,
            height=420,
        )