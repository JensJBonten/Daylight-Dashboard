from __future__ import annotations

from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api.typing import NaTType

DATA_FILE = Path("data") / "Dagens lengde (2).xlsx"
NORMALIZED_COLUMNS = {
    "Dato": "date",
    "Lengde": "day_length",
    "Sol opp": "sunrise",
    "Sol Ned": "sunset",
    "Dagens lengeøkning\ni min, per sist målt dato": "change_since_previous_check_in",
    "Total økning siden start\nav måling pr/min:": "change_since_first_measurement",
}


def load_daylight_data(file_path: Path) -> pd.DataFrame:
    """Load the Excel file and normalize the columns used by the project."""
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find Excel file: {file_path}")

    daylight_dataframe = pd.read_excel(file_path)
    missing_columns = [
        column
        for column in NORMALIZED_COLUMNS
        if column not in daylight_dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"Excel file is missing expected columns: {missing}")

    daylight_dataframe = daylight_dataframe.rename(
        columns=NORMALIZED_COLUMNS
    )
    daylight_dataframe["date"] = pd.to_datetime(
        daylight_dataframe["date"],
        format="%d.%m.%y",
    )

    # Excel times may be represented as decimals, strings, datetime, or time.
    time_columns = (
        "day_length",
        "sunrise",
        "sunset",
        "change_since_previous_check_in",
        "change_since_first_measurement",
    )
    for column in time_columns:
        daylight_dataframe[column] = daylight_dataframe[column].map(
            to_excel_timedelta
        )

    return daylight_dataframe.sort_values("date").reset_index(drop=True)


def to_excel_timedelta(value: Any) -> pd.Timedelta | NaTType:
    """Convert an Excel-like time value to pandas Timedelta."""
    if pd.isna(value):
        return pd.NaT

    if isinstance(value, pd.Timedelta):
        return value

    if isinstance(value, timedelta):
        return pd.Timedelta(value)

    if isinstance(value, (datetime, time)):
        return pd.Timedelta(
            hours=value.hour,
            minutes=value.minute,
            seconds=value.second,
            microseconds=value.microsecond,
        )

    if isinstance(value, (int, float)):
        return pd.to_timedelta(value, unit="D")

    if isinstance(value, str):
        # Excel decimals may use either a comma or a period separator.
        stripped = value.strip()
        try:
            numeric_value = float(stripped.replace(",", "."))
        except ValueError:
            return pd.to_timedelta(stripped)
        return pd.to_timedelta(numeric_value, unit="D")

    raise TypeError(
        f"Unsupported Excel time value: {value!r} "
        f"({type(value)!r})"
    )