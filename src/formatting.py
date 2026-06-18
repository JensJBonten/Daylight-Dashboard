from __future__ import annotations

from datetime import datetime

import pandas as pd


def format_duration(value: pd.Timedelta) -> str:
    """Formaterer en Timedelta som HH:MM:SS."""

    if pd.isna(value):
        return "N/A"

    total_seconds = int(value.total_seconds())
    sign = "-" if total_seconds < 0 else ""

    absolute_seconds = abs(total_seconds)
    hours, remainder = divmod(absolute_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_time_for_display(time_value: str) -> str:
    """Formaterer MET ISO-tid eller HH:MM:SS til HH:MM."""

    if "T" in time_value:
        return datetime.fromisoformat(time_value).strftime("%H:%M")

    return time_value[:5]

def format_date_for_display(date_value: str) -> str:
    """Formaterer en ISO-dato som DD.MM.YYYY."""

    return datetime.fromisoformat(date_value).strftime("%d.%m.%Y")


def _duration_to_seconds(duration_value: str) -> int:
    """Gjør en signert HH:MM:SS-verdi om til sekunder."""

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
    """Formaterer dagslengde som timer og minutter."""

    total_seconds = _duration_to_seconds(duration_value)
    total_minutes = abs(total_seconds) // 60

    hours, minutes = divmod(total_minutes, 60)
    sign = "-" if total_seconds < 0 else ""

    return f"{sign}{hours} t {minutes} min"
    
def format_change_for_display(duration_value: str) -> str:
    """Formaterer en endring med tydelig fortegn."""

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