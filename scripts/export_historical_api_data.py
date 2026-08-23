from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE_FILE = PROJECT_ROOT / "data" / "daylight.db"
DEFAULT_MEASUREMENTS_FILE = (
    PROJECT_ROOT / "data" / "historical_api_measurements.csv"
)
DEFAULT_CHECK_INS_FILE = PROJECT_ROOT / "data" / "historical_check_ins.csv"

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
CHECK_IN_FIELDS = ("date", "location_name")


def _write_csv(
    output_file: Path,
    field_names: tuple[str, ...],
    rows: list[sqlite3.Row],
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)


def export_historical_api_data(
    database_file: Path = DEFAULT_DATABASE_FILE,
    measurements_file: Path = DEFAULT_MEASUREMENTS_FILE,
    check_ins_file: Path = DEFAULT_CHECK_INS_FILE,
) -> tuple[int, int]:
    """Export deterministic API measurement and check-in seed files."""

    if not database_file.is_file():
        raise FileNotFoundError(
            f"Local SQLite database does not exist: {database_file}"
        )

    database_uri = f"file:{database_file.resolve()}?mode=ro"
    with sqlite3.connect(database_uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row
        measurements = connection.execute(
            """
            SELECT
                date,
                location_name,
                day_length,
                sunrise,
                sunset,
                daily_increase,
                total_increase,
                source
            FROM daylight_measurements
            WHERE source = 'api'
            ORDER BY date, location_name
            """
        ).fetchall()
        check_ins = connection.execute(
            """
            SELECT DISTINCT date, location_name
            FROM daylight_check_ins
            ORDER BY date, location_name
            """
        ).fetchall()

    _write_csv(measurements_file, MEASUREMENT_FIELDS, measurements)
    _write_csv(check_ins_file, CHECK_IN_FIELDS, check_ins)
    return len(measurements), len(check_ins)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export local API measurements and historical check-ins."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_FILE,
        help="Path to the local daylight SQLite database.",
    )
    parser.add_argument(
        "--measurements-output",
        type=Path,
        default=DEFAULT_MEASUREMENTS_FILE,
        help="Destination CSV for API measurements.",
    )
    parser.add_argument(
        "--check-ins-output",
        type=Path,
        default=DEFAULT_CHECK_INS_FILE,
        help="Destination CSV for historical check-ins.",
    )
    arguments = parser.parse_args()

    try:
        measurement_count, check_in_count = export_historical_api_data(
            database_file=arguments.database,
            measurements_file=arguments.measurements_output,
            check_ins_file=arguments.check_ins_output,
        )
    except (FileNotFoundError, sqlite3.Error) as error:
        parser.exit(1, f"Export failed: {error}\n")

    print(
        f"Exported {measurement_count} API measurements to "
        f"{arguments.measurements_output}"
    )
    print(
        f"Exported {check_in_count} historical check-ins to "
        f"{arguments.check_ins_output}"
    )


if __name__ == "__main__":
    main()
