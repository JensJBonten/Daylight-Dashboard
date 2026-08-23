from __future__ import annotations

import pandas as pd

try:
    from .formatting import format_duration
    from .measurement import DaylightMeasurement
except ImportError:
    from formatting import format_duration
    from measurement import DaylightMeasurement



def measurements_from_dataframe(
    daylight_dataframe: pd.DataFrame,
    location_name: str,
) -> list[DaylightMeasurement]:
    """Convert normalized DataFrame rows to measurement objects."""
    measurements: list[DaylightMeasurement] = []

    for _, measurement_row in daylight_dataframe.iterrows():
        measurement = DaylightMeasurement(
            date=measurement_row["date"].date().isoformat(),
            location_name=location_name,
            day_length=format_duration(measurement_row["day_length"]),
            sunrise=format_duration(measurement_row["sunrise"]),
            sunset=format_duration(measurement_row["sunset"]),
            daily_increase=format_duration(
                measurement_row["daily_increase"]
            ),
            total_increase=format_duration(
                measurement_row["total_increase"]
            ),
        )

        measurements.append(measurement)

    return measurements
