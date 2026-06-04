from __future__ import annotations

from datetime import datetime

import pandas as pd


def format_duration(value: pd.Timedelta) -> str:
    """Formaterer en Timedelta som HH:MM:SS."""

    if pd.isna(value):
        return "N/A"

    total_seconds = int(value.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_time_for_display(time_value: str) -> str:
    """Formaterer MET ISO-tid eller HH:MM:SS til HH:MM."""

    if "T" in time_value:
        return datetime.fromisoformat(time_value).strftime("%H:%M")

    return time_value[:5]