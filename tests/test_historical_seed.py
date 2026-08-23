import csv
import sqlite3

from src.data_loader import DATA_FILE, load_daylight_data
from src.historical_seed import (
    HISTORICAL_GRUA_SOURCE,
    seed_historical_api_measurements,
    seed_historical_check_ins,
    seed_historical_data,
    seed_historical_grua_measurements,
)
from src.measurement import DaylightMeasurement
from src.sqlite_storage import (
    get_latest_check_in_measurement,
    load_check_in_dates,
    load_measurements,
    save_check_in,
    save_measurement,
)


MEASUREMENT_FIELDS = (
    "date",
    "location_name",
    "day_length",
    "sunrise",
    "sunset",
    "daily_increase",
    "total_increase",
    "source",
)


def write_csv(file_path, field_names, rows):
    with file_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(rows)


def api_row(date, location_name="Oslo", day_length="12:00:00"):
    return {
        "date": date,
        "location_name": location_name,
        "day_length": day_length,
        "sunrise": "06:00:00",
        "sunset": "18:00:00",
        "daily_increase": "00:05:00",
        "total_increase": "01:00:00",
        "source": "api",
    }


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


def test_api_history_and_check_ins_are_seeded_into_fresh_database(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_file = tmp_path / "api.csv"
    check_ins_file = tmp_path / "check_ins.csv"
    write_csv(api_file, MEASUREMENT_FIELDS, [api_row("2026-06-17")])
    write_csv(
        check_ins_file,
        ("date", "location_name"),
        [{"date": "2026-06-17", "location_name": "Oslo"}],
    )

    seed_historical_api_measurements(database_file, api_file)
    seed_historical_check_ins(database_file, check_ins_file)

    measurements = load_measurements(database_file)
    assert len(measurements) == 1
    assert measurements[0].date == "2026-06-17"
    assert load_check_in_dates("Oslo", database_file) == ["2026-06-17"]
    with sqlite3.connect(database_file) as connection:
        source = connection.execute(
            "SELECT source FROM daylight_measurements"
        ).fetchone()
    assert source == ("api",)


def test_complete_historical_seed_is_idempotent_and_histories_coexist(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_file = tmp_path / "api.csv"
    check_ins_file = tmp_path / "check_ins.csv"
    write_csv(api_file, MEASUREMENT_FIELDS, [api_row("2026-06-17")])
    write_csv(
        check_ins_file,
        ("date", "location_name"),
        [{"date": "2026-06-17", "location_name": "Oslo"}],
    )

    for _ in range(2):
        seed_historical_data(
            database_file=database_file,
            api_file=api_file,
            check_ins_file=check_ins_file,
        )

    measurements = load_measurements(database_file)
    assert len(measurements) == len(load_daylight_data(DATA_FILE)) + 1
    assert {measurement.location_name for measurement in measurements} == {
        "Grua",
        "Oslo",
    }
    assert load_check_in_dates("Oslo", database_file) == ["2026-06-17"]


def test_existing_runtime_measurement_wins_over_seed_conflict(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_file = tmp_path / "api.csv"
    runtime_measurement = DaylightMeasurement(
        date="2026-06-17",
        location_name="Oslo",
        day_length="13:37:00",
        sunrise="05:30:00",
        sunset="19:07:00",
        daily_increase="00:10:00",
        total_increase="02:00:00",
    )
    save_measurement(runtime_measurement, database_file, source="api")
    write_csv(
        api_file,
        MEASUREMENT_FIELDS,
        [api_row("2026-06-17", day_length="12:00:00")],
    )

    seed_historical_api_measurements(database_file, api_file)

    assert load_measurements(database_file) == [runtime_measurement]


def test_seeded_check_ins_work_for_previous_check_in_lookup(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_file = tmp_path / "api.csv"
    check_ins_file = tmp_path / "check_ins.csv"
    write_csv(
        api_file,
        MEASUREMENT_FIELDS,
        [
            api_row("2026-06-17", day_length="12:00:00"),
            api_row("2026-06-18", day_length="12:05:00"),
        ],
    )
    write_csv(
        check_ins_file,
        ("date", "location_name"),
        [
            {"date": "2026-06-17", "location_name": "Oslo"},
            {"date": "2026-06-18", "location_name": "Oslo"},
        ],
    )
    seed_historical_api_measurements(database_file, api_file)
    seed_historical_check_ins(database_file, check_ins_file)

    previous = get_latest_check_in_measurement(
        "Oslo",
        before_date="2026-06-18",
        database_file=database_file,
    )

    assert previous is not None
    assert previous.date == "2026-06-17"
    assert previous.day_length == "12:00:00"


def test_complete_seed_reconciles_stale_runtime_check_in(tmp_path):
    database_file = tmp_path / "daylight.db"
    api_file = tmp_path / "api.csv"
    check_ins_file = tmp_path / "check_ins.csv"
    current_measurement = DaylightMeasurement(
        date="2026-08-23",
        location_name="Oslo",
        day_length="14:00:00",
        sunrise="06:00:00",
        sunset="20:00:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )
    save_measurement(current_measurement, database_file, source="api")
    save_check_in("Oslo", "2026-08-23", database_file)
    write_csv(
        api_file,
        MEASUREMENT_FIELDS,
        [
            api_row("2026-08-20", day_length="16:00:00"),
            api_row("2026-08-21", day_length="15:00:00"),
            api_row("2026-08-22", day_length="14:30:00"),
            api_row("2026-08-23", day_length="13:00:00"),
        ],
    )
    write_csv(
        check_ins_file,
        ("date", "location_name"),
        [{"date": "2026-08-21", "location_name": "Oslo"}],
    )

    seed_historical_data(
        database_file=database_file,
        api_file=api_file,
        check_ins_file=check_ins_file,
    )

    with sqlite3.connect(database_file) as connection:
        current_result = connection.execute(
            """
            SELECT day_length, daily_increase, total_increase, source
            FROM daylight_measurements
            WHERE date = '2026-08-23' AND location_name = 'Oslo'
            """
        ).fetchone()
    assert current_result == ("14:00:00", "-01:00:00", "-02:00:00", "api")
