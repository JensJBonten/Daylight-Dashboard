import csv

import pytest

from scripts.export_historical_api_data import export_historical_api_data
from src.measurement import DaylightMeasurement
from src.sqlite_storage import save_check_in, save_measurement


def test_export_is_sorted_repeatable_and_excludes_excel_rows(tmp_path):
    database_file = tmp_path / "daylight.db"
    measurements_file = tmp_path / "measurements.csv"
    check_ins_file = tmp_path / "check_ins.csv"
    api_measurement = DaylightMeasurement(
        date="2026-06-18",
        location_name="Oslo",
        day_length="12:05:00",
        sunrise="05:58:00",
        sunset="18:03:00",
        daily_increase="00:05:00",
        total_increase="01:05:00",
    )
    excel_measurement = DaylightMeasurement(
        date="2026-01-22",
        location_name="Grua",
        day_length="07:09:00",
        sunrise="08:54:00",
        sunset="16:04:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )
    save_measurement(api_measurement, database_file, source="api")
    save_measurement(excel_measurement, database_file, source="excel")
    save_check_in("Oslo", "2026-06-18", database_file)

    counts = export_historical_api_data(
        database_file,
        measurements_file,
        check_ins_file,
    )
    first_contents = (measurements_file.read_bytes(), check_ins_file.read_bytes())
    export_historical_api_data(database_file, measurements_file, check_ins_file)

    assert counts == (1, 1)
    assert first_contents == (
        measurements_file.read_bytes(),
        check_ins_file.read_bytes(),
    )
    with measurements_file.open(encoding="utf-8", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))
    assert rows[0]["date"] == api_measurement.date
    assert rows[0]["source"] == "api"


def test_export_fails_clearly_when_database_is_missing(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        export_historical_api_data(
            database_file=tmp_path / "missing.db",
            measurements_file=tmp_path / "measurements.csv",
            check_ins_file=tmp_path / "check_ins.csv",
        )
