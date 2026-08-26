from __future__ import annotations

from datetime import date

import streamlit as st

from dashboard_styles import apply_season_sidebar_style
from reference_data import (
    ReferenceDataError,
    load_reference_data,
)
from seasonal import (
    SeasonTheme,
    calculate_change_since_solstice,
    get_next_solstice,
    get_season_theme,
)


def render_season_overview(
    selected_location: str,
) -> tuple[SeasonTheme, float | None]:
    """Render the active season and return its theme and solstice change."""

    today = date.today()

    # Previewing a season changes only the visual theme.
    season_preview_dates = {
        "Automatisk – dagens dato": today,
        "❄️ Vinter": date(
            today.year,
            1,
            15,
        ),
        "🌱 Vår": date(
            today.year,
            4,
            15,
        ),
        "☀️ Sommer": date(
            today.year,
            7,
            15,
        ),
        "🍂 Høst": date(
            today.year,
            9,
            15,
        ),
        "🎃 Halloween": date(
            today.year,
            10,
            15,
        ),
        "🎅 Jul": date(
            today.year,
            12,
            15,
        ),
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

