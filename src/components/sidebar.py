from __future__ import annotations

from datetime import date

import streamlit as st

from api_client import (
    get_api_location_by_name,
    get_api_locations,
)
from measurement_service import (
    DaylightServiceError,
    fetch_and_save_measurement,
)
from sqlite_storage import load_check_in_dates


def render_sidebar_controls() -> str:
    """Render location selection and today's check-in control."""

    available_locations = sorted(
        get_api_locations().keys()
    )

    default_location_index = (
        available_locations.index("Oslo")
    )

    today = date.today()
    today_iso = today.isoformat()

    with st.sidebar:
        st.header("Kontroller")

        selected_location = st.selectbox(
            "Sted",
            options=available_locations,
            index=default_location_index,
        )

        check_in_dates = load_check_in_dates(
            selected_location
        )

        already_checked_in_today = (
            today_iso in check_in_dates
        )

        st.caption(
            "Henter dagens dagslysdata fra MET og registrerer "
            "dagens felles måling."
        )

        if check_in_dates:
            latest_check_in = max(
                check_in_dates
            )

            formatted_latest_check_in = (
                date.fromisoformat(
                    latest_check_in
                ).strftime(
                    "%d.%m.%Y"
                )
            )

            if already_checked_in_today:
                st.caption(
                    "✓ Dagens måling er allerede registrert."
                )
            else:
                st.caption(
                    "Sist innsjekket: "
                    f"{formatted_latest_check_in}"
                )
        else:
            st.caption(
                "Ingen innsjekkinger ennå."
            )

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
            location = get_api_location_by_name(
                selected_location
            )

            try:
                with st.spinner(
                    "Henter dagslysdata!"
                ):
                    measurement = (
                        fetch_and_save_measurement(
                            location,
                            today,
                        )
                    )

            except DaylightServiceError:
                st.error(
                    "Kunne ikke hente eller lagre dagslysdataen. "
                    "Kontroller nettforbindelsen og prøv igjen."
                )

            else:
                formatted_date = (
                    date.fromisoformat(
                        measurement.date
                    ).strftime(
                        "%d.%m.%Y"
                    )
                )

                st.session_state[
                    "daylight_success_message"
                ] = (
                    "Innsjekking registrert for "
                    f"{measurement.location_name} "
                    f"{formatted_date}."
                )

                st.rerun()

    return selected_location

