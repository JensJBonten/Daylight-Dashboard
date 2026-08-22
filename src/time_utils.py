from __future__ import annotations

from datetime import timedelta


def parse_duration(duration: str) -> timedelta:
    """Convert a positive or negative HH:MM:SS value to timedelta."""

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
    """Format a timedelta as a signed HH:MM:SS value."""

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
    """Calculate the difference between two HH:MM:SS values."""

    difference = (
        parse_duration(new_duration)
        - parse_duration(old_duration)
    )

    return format_timedelta(difference)
