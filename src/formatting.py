from __future__ import annotations

from datetime import datetime

import pandas as pd


def format_duration(value: pd.Timedelta) -> str:
    """Format a Timedelta as HH:MM:SS."""

    if pd.isna(value):
        return "N/A"

    total_seconds = int(value.total_seconds())
    sign = "-" if total_seconds < 0 else ""

    absolute_seconds = abs(total_seconds)
    hours, remainder = divmod(absolute_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_time_for_display(time_value: str) -> str:
    """Format a MET ISO time or HH:MM:SS value as HH:MM."""

    if "T" in time_value:
        return datetime.fromisoformat(time_value).strftime("%H:%M")

    return time_value[:5]


def format_date_for_display(date_value: str) -> str:
    """Format an ISO date as DD.MM.YYYY."""

    return datetime.fromisoformat(date_value).strftime("%d.%m.%Y")


def _duration_to_seconds(duration_value: str) -> int:
    """Convert a signed HH:MM:SS value to seconds."""

    sign = -1 if duration_value.startswith("-") else 1
    normalized_duration = duration_value.lstrip("+-")

    hours, minutes, seconds = map(
        int,
        normalized_duration.split(":"),
    )

    return sign * (
        hours * 3600
        + minutes * 60
        + seconds
    )


def format_duration_for_display(duration_value: str) -> str:
    """Format day length as hours and minutes."""

    total_seconds = _duration_to_seconds(duration_value)
    total_minutes = abs(total_seconds) // 60

    hours, minutes = divmod(total_minutes, 60)
    sign = "-" if total_seconds < 0 else ""

    return f"{sign}{hours} t {minutes} min"


def format_change_for_display(duration_value: str) -> str:
    """Format a duration change with an explicit sign."""

    total_seconds = _duration_to_seconds(duration_value)

    if total_seconds == 0:
        return "0 min"

    sign = "+" if total_seconds > 0 else "-"
    total_minutes = abs(total_seconds) // 60
    hours, minutes = divmod(total_minutes, 60)

    if hours and minutes:
        readable_duration = f"{hours} t {minutes} min"
    elif hours:
        readable_duration = f"{hours} t"
    else:
        readable_duration = f"{minutes} min"

    return f"{sign}{readable_duration}"


def format_change_as_story(
    duration_value: str,
) -> str:
    """Format a duration change as a readable daylight story."""

    total_seconds = _duration_to_seconds(
        duration_value
    )

    if total_seconds == 0:
        return "Ingen endring"

    readable_duration = format_change_for_display(
        duration_value
    ).lstrip("+-−").strip()

    direction = (
        "lengre"
        if total_seconds > 0
        else "kortere"
    )

    return f"{readable_duration} {direction}"