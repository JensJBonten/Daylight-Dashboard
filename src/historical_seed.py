from __future__ import annotations

import csv
from pathlib import Path

try:
    from .data_loader import DATA_FILE, load_daylight_data
    from .measurement import DaylightMeasurement
    from .measurement_mapper import measurements_from_dataframe
    from .sqlite_storage import (
        DATABASE_FILE,
        has_measurements_from_source,
        save_check_in,
        save_measurements,
    )
except ImportError:
    from data_loader import DATA_FILE, load_daylight_data
    from measurement import DaylightMeasurement
    from measurement_mapper import measurements_from_dataframe
    from sqlite_storage import (
        DATABASE_FILE,
        has_measurements_from_source,
        save_check_in,
        save_measurements,
    )


HISTORICAL_GRUA_SOURCE = "historical_grua_excel"
HISTORICAL_API_FILE = Path("data") / "historical_api_measurements.csv"
HISTORICAL_CHECK_INS_FILE = Path("data") / "historical_check_ins.csv"


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


def seed_historical_api_measurements(
    database_file: Path = DATABASE_FILE,
    data_file: Path = HISTORICAL_API_FILE,
) -> None:
    """Seed exported API history without replacing deployed measurements."""

    with data_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    for row in rows:
        measurement = DaylightMeasurement.from_dict(row)
        save_measurements(
            [measurement],
            database_file=database_file,
            source=row["source"],
            overwrite_existing=False,
        )


def seed_historical_check_ins(
    database_file: Path = DATABASE_FILE,
    data_file: Path = HISTORICAL_CHECK_INS_FILE,
) -> None:
    """Seed exported shared check-ins without changing existing check-ins."""

    with data_file.open(encoding="utf-8", newline="") as csv_file:
        rows = csv.DictReader(csv_file)
        for row in rows:
            save_check_in(
                location_name=row["location_name"],
                check_in_date=row["date"],
                database_file=database_file,
                overwrite_existing=False,
            )


def seed_historical_data(
    database_file: Path = DATABASE_FILE,
    excel_file: Path = DATA_FILE,
    api_file: Path = HISTORICAL_API_FILE,
    check_ins_file: Path = HISTORICAL_CHECK_INS_FILE,
) -> None:
    """Seed all bundled history into a fresh deployment database."""

    seed_historical_api_measurements(database_file, api_file)
    seed_historical_grua_measurements(database_file, excel_file)
    seed_historical_check_ins(database_file, check_ins_file)
