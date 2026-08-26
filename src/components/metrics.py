from __future__ import annotations

from datetime import date

import streamlit as st

from formatting import (
    format_change_as_story,
    format_date_for_display,
    format_duration_for_display,
    format_time_for_display,
)
from measurement import DaylightMeasurement
from seasonal import (
    format_hours_change_as_story,
    get_previous_solstice,
)
from sqlite_storage import load_check_in_dates


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
        f"▥ Siden {previous_solstice.name.lower()}"
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
        change_label = "▥ Siden siste innsjekk"
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
            "◷ Dagslengde",
            format_duration_for_display(
                latest_measurement.day_length
            ),
        ),
        (
            "☀ Soloppgang",
            format_time_for_display(
                latest_measurement.sunrise
            ),
        ),
        (
            "◐ Solnedgang",
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

