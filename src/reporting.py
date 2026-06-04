from __future__ import annotations

import pandas as pd

from .formatting import format_duration


def build_summary(daylight_dataframe: pd.DataFrame) -> list[str]:
    """Bygger en kort oppsummering av det innlastede datasettet."""

    first_measurement_row = daylight_dataframe.iloc[0]
    last_measurement_row = daylight_dataframe.iloc[-1]

    return [
        f"Rows: {len(daylight_dataframe)}",
        f"Date range: {first_measurement_row['date'].date()} -> {last_measurement_row['date'].date()}",
        f"Day length: {format_duration(first_measurement_row['day_length'])} -> {format_duration(last_measurement_row['day_length'])}",
        f"Sunrise: {format_duration(first_measurement_row['sunrise'])} -> {format_duration(last_measurement_row['sunrise'])}",
        f"Sunset: {format_duration(first_measurement_row['sunset'])} -> {format_duration(last_measurement_row['sunset'])}",
        f"Total increase: {format_duration(last_measurement_row['total_increase'])}",
        f"Largest daily increase: {format_duration(daylight_dataframe['daily_increase'].max())}",
    ]


def print_preview(daylight_dataframe: pd.DataFrame, row_count: int) -> None:
    """Skriver ut de første radene som en lesbar og formatert tabell."""

    if row_count <= 0:
        return

    preview_dataframe = daylight_dataframe.head(row_count).copy()

    for column in ("day_length", "sunrise", "sunset", "daily_increase", "total_increase"):
        preview_dataframe[column] = preview_dataframe[column].map(format_duration)

    print("\nPreview:")
    print(preview_dataframe.to_string(index=False))