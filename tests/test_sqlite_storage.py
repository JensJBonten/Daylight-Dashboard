from src.measurement import DaylightMeasurement
from src.sqlite_storage import (
    get_first_measurement_for_location,
    get_latest_check_in_measurement,
    get_latest_measurement,
    get_previous_measurement_for_location,
    initialize_database,
    load_check_in_dates,
    load_measurements,
    save_check_in,
    save_measurements,
)


def test_save_and_load_measurements_from_sqlite(tmp_path):
    """Check that measurements can be saved to and loaded from SQLite."""

    database_file = tmp_path / "daylight.db"

    measurements = [
        DaylightMeasurement(
            date="2026-03-09",
            location_name="Grua",
            day_length="11:11:00",
            sunrise="06:52:00",
            sunset="18:04:00",
            daily_increase="00:16:00",
            total_increase="04:02:00",
        ),
        DaylightMeasurement(
            date="2026-03-10",
            location_name="Grua",
            day_length="11:17:00",
            sunrise="06:49:00",
            sunset="18:06:00",
            daily_increase="00:06:00",
            total_increase="04:08:00",
        ),
    ]

    initialize_database(database_file)
    save_measurements(measurements, database_file=database_file)

    loaded_measurements = load_measurements(database_file=database_file)
    latest_measurement = get_latest_measurement(database_file=database_file)

    assert len(loaded_measurements) == 2
    assert loaded_measurements[0].date == "2026-03-09"
    assert loaded_measurements[1].date == "2026-03-10"

    assert latest_measurement is not None
    assert latest_measurement.date == "2026-03-10"
    assert latest_measurement.location_name == "Grua"
    assert latest_measurement.total_increase == "04:08:00"


def test_get_previous_and_first_measurement_for_location(tmp_path):
    """Check that SQLite can find previous and first measurements for a location."""

    database_file = tmp_path / "daylight.db"

    measurements = [
        DaylightMeasurement(
            date="2026-01-22",
            location_name="Grua",
            day_length="07:09:00",
            sunrise="08:54:00",
            sunset="16:04:00",
            daily_increase="00:00:00",
            total_increase="00:00:00",
        ),
        DaylightMeasurement(
            date="2026-03-10",
            location_name="Grua",
            day_length="11:17:00",
            sunrise="06:49:00",
            sunset="18:06:00",
            daily_increase="00:06:00",
            total_increase="04:08:00",
        ),
        DaylightMeasurement(
            date="2026-03-10",
            location_name="Oslo",
            day_length="11:25:00",
            sunrise="06:42:00",
            sunset="18:07:00",
            daily_increase="00:06:00",
            total_increase="04:10:00",
        ),
    ]

    save_measurements(measurements, database_file=database_file)

    previous_measurement = get_previous_measurement_for_location(
        location_name="Grua",
        measurement_date="2026-06-03",
        database_file=database_file,
    )

    first_measurement = get_first_measurement_for_location(
        location_name="Grua",
        database_file=database_file,
    )

    assert previous_measurement is not None
    assert previous_measurement.date == "2026-03-10"
    assert previous_measurement.location_name == "Grua"
    assert previous_measurement.day_length == "11:17:00"

    assert first_measurement is not None
    assert first_measurement.date == "2026-01-22"
    assert first_measurement.location_name == "Grua"
    assert first_measurement.day_length == "07:09:00"


def test_check_in_is_unique_per_location_and_date(
    tmp_path,
):
    database_file = tmp_path / "daylight.db"

    save_check_in(
        "Oslo",
        "2026-08-21",
        database_file,
    )
    save_check_in(
        "Oslo",
        "2026-08-21",
        database_file,
    )
    save_check_in(
        "Bergen",
        "2026-08-21",
        database_file,
    )

    assert load_check_in_dates(
        "Oslo",
        database_file,
    ) == ["2026-08-21"]

    assert load_check_in_dates(
        "Bergen",
        database_file,
    ) == ["2026-08-21"]

def test_get_latest_check_in_measurement(
    tmp_path,
):
    """Return the latest measurement with a real check-in."""

    database_file = (
        tmp_path
        / "daylight.db"
    )

    measurements = [
        DaylightMeasurement(
            date="2026-08-01",
            location_name="Oslo",
            day_length="16:10:00",
            sunrise="04:55:00",
            sunset="21:05:00",
            daily_increase="00:00:00",
            total_increase="00:00:00",
        ),
        DaylightMeasurement(
            date="2026-08-10",
            location_name="Oslo",
            day_length="15:30:00",
            sunrise="05:16:00",
            sunset="20:46:00",
            daily_increase="-00:40:00",
            total_increase="-00:40:00",
        ),
        DaylightMeasurement(
            date="2026-08-17",
            location_name="Oslo",
            day_length="14:44:00",
            sunrise="05:34:00",
            sunset="20:18:00",
            daily_increase="-00:46:00",
            total_increase="-01:26:00",
        ),
    ]

    save_measurements(
        measurements,
        database_file=database_file,
    )

    save_check_in(
        location_name="Oslo",
        check_in_date="2026-08-01",
        database_file=database_file,
    )

    # Målingen 10. august lagres, men registreres
    # med vilje ikke som en innsjekking.
    save_check_in(
        location_name="Oslo",
        check_in_date="2026-08-17",
        database_file=database_file,
    )

    result = (
        get_latest_check_in_measurement(
            location_name="Oslo",
            before_date="2026-08-17",
            database_file=database_file,
        )
    )

    assert result is not None
    assert result.date == "2026-08-01"
    assert result.day_length == "16:10:00"
