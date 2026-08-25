from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class Solstice:
    """Represent one solstice reference date."""

    name: str
    date: date
    icon: str


@dataclass(frozen=True)
class SeasonTheme:
    """Represent the visual theme for one season."""

    name: str
    icon: str
    accent: str
    background: str


def get_solstices(
    year: int,
) -> tuple[Solstice, Solstice]:
    """Return summer and winter solstice reference dates."""

    return (
        Solstice(
            name="Sommersolverv",
            date=date(year, 6, 21),
            icon="☀️",
        ),
        Solstice(
            name="Vintersolverv",
            date=date(year, 12, 21),
            icon="❄️",
        ),
    )


def get_next_solstice(
    today: date,
) -> Solstice:
    """Return the next solstice, including today."""

    summer, winter = get_solstices(
        today.year
    )

    if today <= summer.date:
        return summer

    if today <= winter.date:
        return winter

    next_summer, _ = get_solstices(
        today.year + 1
    )

    return next_summer


def get_previous_solstice(
    today: date,
) -> Solstice:
    """Return the latest solstice on or before today."""

    summer, winter = get_solstices(
        today.year
    )

    if today >= winter.date:
        return winter

    if today >= summer.date:
        return summer

    _, previous_winter = get_solstices(
        today.year - 1
    )

    return previous_winter


def get_season_theme(
    target_date: date,
) -> SeasonTheme:
    """Return the seasonal theme for a date."""

    month = target_date.month

    if month == 10:
        return SeasonTheme(
            name="Halloween",
            icon="🎃",
            background="#FFF1E3",
            accent="#C86A1E",
        )

    if month in (11, 12):
        return SeasonTheme(
            name="Jul",
            icon="🎅",
            background="#F4F8F0",
            accent="#B84A3A",
        )

    if month in (1, 2):
        return SeasonTheme(
            name="Vinter",
            icon="❄️",
            background="#EAF4FF",
            accent="#7DA6D9",
        )

    if month in (3, 4, 5):
        return SeasonTheme(
            name="Vår",
            icon="🌱",
            background="#EEF7E8",
            accent="#6FAE57",
        )

    if month in (6, 7, 8):
        return SeasonTheme(
            name="Sommer",
            icon="☀️",
            background="#FFF8D9",
            accent="#D9B338",
        )

    return SeasonTheme(
        name="Høst",
        icon="🍂",
        background="#FFF0E0",
        accent="#C97A2B",
    )


def find_nearest_reference_row(
    reference_data: pd.DataFrame,
    target_date: date,
) -> pd.Series:
    """Return the weekly reference row nearest a date."""

    if reference_data.empty:
        raise ValueError(
            "Reference data cannot be empty."
        )

    target_timestamp = pd.Timestamp(
        target_date
    )

    distances = (
        reference_data["date"]
        - target_timestamp
    ).abs()

    return reference_data.loc[
        distances.idxmin()
    ]


def calculate_change_since_solstice(
    reference_data: pd.DataFrame,
    today: date,
) -> float | None:
    """Calculate daylight change since the previous solstice."""

    if reference_data.empty:
        return None

    previous_solstice = get_previous_solstice(
        today
    )

    reference_years = set(
        reference_data["date"].dt.year
    )

    if (
        previous_solstice.date.year
        not in reference_years
    ):
        return None

    solstice_row = find_nearest_reference_row(
        reference_data,
        previous_solstice.date,
    )

    distance_from_solstice = abs(
        (
            solstice_row["date"].date()
            - previous_solstice.date
        ).days
    )

    # Weekly reference points may fall before or after the exact solstice date.
    if distance_from_solstice > 7:
        return None

    available_data = reference_data[
        reference_data["date"]
        <= pd.Timestamp(today)
    ]

    if available_data.empty:
        return None

    latest_row = available_data.loc[
        available_data["date"].idxmax()
    ]

    return float(
        latest_row["daylight_hours"]
        - solstice_row["daylight_hours"]
    )


def format_hours_change(
    change_in_hours: float,
) -> str:
    """Format decimal hours as signed hours and minutes."""

    total_minutes = round(
        abs(change_in_hours) * 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if change_in_hours > 0:
        sign = "+"
    elif change_in_hours < 0:
        sign = "−"
    else:
        sign = ""

    parts: list[str] = []

    if hours:
        parts.append(f"{hours} t")

    if minutes or not parts:
        parts.append(f"{minutes} min")

    return sign + " ".join(parts)

def format_hours_change_as_story(
    change_in_hours: float,
) -> str:
    """Format a decimal-hour change as a readable daylight story."""

    total_minutes = round(
        change_in_hours * 60
    )

    if total_minutes == 0:
        return "Ingen endring"

    readable_duration = format_hours_change(
        change_in_hours
    ).lstrip("+−-").strip()

    direction = (
        "lengre"
        if total_minutes > 0
        else "kortere"
    )

    return f"{readable_duration} {direction}"