from __future__ import annotations

from datetime import timedelta


def parse_duration(duration: str) -> timedelta:
    """Gjør en positiv eller negativ HH:MM:SS-verdi om til timedelta."""

    sign = -1 if duration.startswith("-") else 1
    normalized_duration = duration.lstrip("+-")

    hours, minutes, seconds = normalized_duration.split(":")

    parsed_duration = timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
    )

    return sign * parsed_duration


def format_timedelta(duration: timedelta) -> str:
    """Formaterer timedelta som en signert HH:MM:SS-verdi."""

    total_seconds = int(duration.total_seconds())
    sign = "-" if total_seconds < 0 else ""

    absolute_seconds = abs(total_seconds)
    hours, remainder = divmod(absolute_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{sign}{hours:02d}:{minutes:02d}:{seconds:02d}"


def calculate_duration_difference(
    new_duration: str,
    old_duration: str,
) -> str:
    """Beregner forskjellen mellom to HH:MM:SS-verdier."""

    difference = (
        parse_duration(new_duration)
        - parse_duration(old_duration)
    )

    return format_timedelta(difference)