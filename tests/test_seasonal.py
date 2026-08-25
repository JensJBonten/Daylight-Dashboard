from datetime import date

import pandas as pd
import pytest

from src.seasonal import (
    calculate_change_since_solstice,
    format_hours_change,
    get_next_solstice,
    get_season_theme,
    format_hours_change_as_story,
)


@pytest.mark.parametrize(
    (
        "selected_date",
        "expected_name",
        "expected_icon",
    ),
    [
        (
            date(2026, 1, 15),
            "Vinter",
            "❄️",
        ),
        (
            date(2026, 4, 15),
            "Vår",
            "🌱",
        ),
        (
            date(2026, 7, 15),
            "Sommer",
            "☀️",
        ),
        (
            date(2026, 9, 15),
            "Høst",
            "🍂",
        ),
        (
            date(2026, 10, 15),
            "Halloween",
            "🎃",
        ),
        (
            date(2026, 11, 15),
            "Jul",
            "🎅",
        ),
        (
            date(2026, 12, 15),
            "Jul",
            "🎅",
        ),
    ],
)
def test_season_theme_for_date(
    selected_date,
    expected_name,
    expected_icon,
):
    theme = get_season_theme(
        selected_date
    )

    assert theme.name == expected_name
    assert theme.icon == expected_icon


def test_next_solstice_in_august_is_winter():
    result = get_next_solstice(
        date(2026, 8, 22)
    )

    assert result.name == "Vintersolverv"
    assert result.date == date(
        2026,
        12,
        21,
    )


def test_next_solstice_after_christmas_is_next_summer():
    result = get_next_solstice(
        date(2026, 12, 22)
    )

    assert result.name == "Sommersolverv"
    assert result.date == date(
        2027,
        6,
        21,
    )


def test_change_since_summer_solstice():
    reference_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-06-22",
                    "2026-08-17",
                ]
            ),
            "daylight_hours": [
                18.8,
                15.3,
            ],
        }
    )

    result = calculate_change_since_solstice(
        reference_data,
        date(2026, 8, 22),
    )

    assert result == pytest.approx(-3.5)


def test_missing_previous_solstice_returns_none():
    reference_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-01-05",
                    "2026-02-16",
                ]
            ),
            "daylight_hours": [
                6.2,
                9.1,
            ],
        }
    )

    result = calculate_change_since_solstice(
        reference_data,
        date(2026, 2, 20),
    )

    assert result is None


def test_format_negative_hour_change():
    assert (
        format_hours_change(-1.5)
        == "−1 t 30 min"
    )


def test_format_positive_minute_change():
    assert (
        format_hours_change(0.25)
        == "+15 min"
    )
    
def test_format_solstice_change_as_shorter_story():
    assert (
        format_hours_change_as_story(
            -3.5
        )
        == "3 t 30 min kortere"
    )


def test_format_solstice_change_as_longer_story():
    assert (
        format_hours_change_as_story(
            0.25
        )
        == "15 min lengre"
    )


def test_format_solstice_change_story_handles_zero():
    assert (
        format_hours_change_as_story(
            0.0
        )
        == "Ingen endring"
    )