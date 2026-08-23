import sqlite3

from src.data_loader import DATA_FILE, load_daylight_data
from src.historical_seed import (
    HISTORICAL_GRUA_SOURCE,
    seed_historical_grua_measurements,
)
from src.measurement import DaylightMeasurement
from src.sqlite_storage import (
    load_measurements,
    save_measurement,
)


def test_fresh_database_is_seeded_with_historical_grua_data(tmp_path):
    database_file = tmp_path / "daylight.db"

    seed_historical_grua_measurements(database_file=database_file)

    measurements = load_measurements(database_file=database_file)
    assert len(measurements) == len(load_daylight_data(DATA_FILE))
    assert {measurement.location_name for measurement in measurements} == {
        "Grua"
    }


def test_historical_seed_is_idempotent(tmp_path):
    database_file = tmp_path / "daylight.db"

    seed_historical_grua_measurements(database_file=database_file)
    first_count = len(load_measurements(database_file=database_file))
    seed_historical_grua_measurements(database_file=database_file)

    assert len(load_measurements(database_file=database_file)) == first_count


def test_unrelated_api_data_does_not_prevent_historical_seed(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_measurement = DaylightMeasurement(
        date="2026-08-23",
        location_name="Oslo",
        day_length="15:00:00",
        sunrise="05:30:00",
        sunset="20:30:00",
        daily_increase="-00:05:00",
        total_increase="01:00:00",
    )
    save_measurement(
        api_measurement,
        database_file=database_file,
        source="api",
    )

    seed_historical_grua_measurements(database_file=database_file)

    measurements = load_measurements(database_file=database_file)
    assert api_measurement in measurements
    assert any(
        measurement.location_name == "Grua"
        for measurement in measurements
    )
    with sqlite3.connect(database_file) as connection:
        api_source = connection.execute(
            """
            SELECT source FROM daylight_measurements
            WHERE date = ? AND location_name = ?
            """,
            (api_measurement.date, api_measurement.location_name),
        ).fetchone()
        historical_count = connection.execute(
            "SELECT COUNT(*) FROM daylight_measurements WHERE source = ?",
            (HISTORICAL_GRUA_SOURCE,),
        ).fetchone()[0]

    assert api_source == ("api",)
    assert historical_count == len(load_daylight_data(DATA_FILE))
