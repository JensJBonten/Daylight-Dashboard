from __future__ import annotations

import pandas as pd

from .formatting import format_duration
from .measurement import DaylightMeasurement



def measurements_from_dataframe(
    daylight_dataframe: pd.DataFrame, location_name: str,
) -> list[DaylightMeasurement]:
    """
    Gjør rene DataFrame-rader om til DaylightMeasurement-objekter.
    """
    measurements: list[DaylightMeasurement] = []

    # Itererer over hver rad fra data_loader.py.
    # date er allerede konvertert til datetime, og tidskolonnene er pandas Timedelta.
    for _, measurement_row in daylight_dataframe.iterrows():
        measurement = DaylightMeasurement(
            # Dato lagres som ISO-string fordi det er JSON-vennlig og lett å sortere senere.
            date=measurement_row["date"].date().isoformat(),

            # Beholder lokasjonen slik at modellen senere kan fungere med flere steder.
            location_name=location_name,

            # Konverterer Timedelta-verdier til leselige strenger før de lagres.
            day_length=format_duration(measurement_row["day_length"]),
            sunrise=format_duration(measurement_row["sunrise"]),
            sunset=format_duration(measurement_row["sunset"]),
            daily_increase=format_duration(measurement_row["daily_increase"]),
            total_increase=format_duration(measurement_row["total_increase"]),
        )

        measurements.append(measurement)
    return measurements
