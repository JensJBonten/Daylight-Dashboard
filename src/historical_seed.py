from __future__ import annotations

from pathlib import Path

try:
    from .data_loader import DATA_FILE, load_daylight_data
    from .measurement_mapper import measurements_from_dataframe
    from .sqlite_storage import (
        DATABASE_FILE,
        has_measurements_from_source,
        save_measurements,
    )
except ImportError:
    from data_loader import DATA_FILE, load_daylight_data
    from measurement_mapper import measurements_from_dataframe
    from sqlite_storage import (
        DATABASE_FILE,
        has_measurements_from_source,
        save_measurements,
    )


HISTORICAL_GRUA_SOURCE = "historical_grua_excel"


def seed_historical_grua_measurements(
    database_file: Path = DATABASE_FILE,
    data_file: Path = DATA_FILE,
) -> None:
    """Seed the bundled Grua history once without replacing existing rows."""

    if has_measurements_from_source(
        HISTORICAL_GRUA_SOURCE,
        database_file=database_file,
    ):
        return

    daylight_dataframe = load_daylight_data(data_file)
    measurements = measurements_from_dataframe(
        daylight_dataframe,
        location_name="Grua",
    )
    save_measurements(
        measurements,
        database_file=database_file,
        source=HISTORICAL_GRUA_SOURCE,
        overwrite_existing=False,
    )
