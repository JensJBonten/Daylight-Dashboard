from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__:
    from .data_loader import DATA_FILE, load_daylight_data
    from .measurement_mapper import measurements_from_dataframe
    from .plotting import save_plot
    from .reporting import build_summary, print_preview
    from .sqlite_storage import (
        get_latest_measurement as get_latest_sqlite_measurement,
    )
    from .sqlite_storage import (
        save_measurements as save_sqlite_measurements,
    )
    from .storage import get_latest_measurement, save_measurements
else:
    sys.path.append(str(Path(__file__).resolve().parent))
    from data_loader import DATA_FILE, load_daylight_data
    from measurement_mapper import measurements_from_dataframe
    from plotting import save_plot
    from reporting import build_summary, print_preview
    from sqlite_storage import (
        get_latest_measurement as get_latest_sqlite_measurement,
    )
    from sqlite_storage import (
        save_measurements as save_sqlite_measurements,
    )
    from storage import get_latest_measurement, save_measurements


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""

    parser = argparse.ArgumentParser(
        description=(
            "Daylight Measurement Dashboard: analyze daylight development "
            "from the Excel file in data/."
        )
    )

    parser.add_argument(
        "--file",
        type=Path,
        default=DATA_FILE,
        help=f"Path to the Excel file. Default: {DATA_FILE}",
    )

    parser.add_argument(
        "--preview",
        type=int,
        default=5,
        help="Number of rows to print as a preview. Use 0 to disable.",
    )

    parser.add_argument(
        "--plot",
        type=Path,
        help="Optional output path for a PNG chart.",
    )

    parser.add_argument(
        "--location",
        type=str,
        default="Grua",
        help="Location name for the daylight measurements. Default: Grua.",
    )

    parser.add_argument(
        "--save",
        action="store_true",
        help="Save loaded daylight measurements to JSON storage.",
    )

    parser.add_argument(
        "--save-sqlite",
        action="store_true",
        help="Save loaded daylight measurements to SQLite storage.",
    )

    return parser.parse_args()


def print_measurement(
    title: str,
    measurement,
) -> None:
    """Print a DaylightMeasurement in a readable terminal format."""

    print(f"\n{title}:")
    print(f"- Date: {measurement.date}")
    print(f"- Location: {measurement.location_name}")
    print(f"- Day length: {measurement.day_length}")
    print(f"- Sunrise: {measurement.sunrise}")
    print(f"- Sunset: {measurement.sunset}")
    print(f"- Daily increase: {measurement.daily_increase}")
    print(f"- Total increase: {measurement.total_increase}")


def main() -> None:
    """Run the Excel import, reporting, storage, and chart workflow."""

    args = parse_args()

    daylight_dataframe = load_daylight_data(
        args.file
    )

    print("Daylight Measurement Dashboard")
    print("Dataset summary")

    for line in build_summary(
        daylight_dataframe
    ):
        print(f"- {line}")

    print_preview(
        daylight_dataframe,
        args.preview,
    )

    measurements = measurements_from_dataframe(
        daylight_dataframe,
        location_name=args.location,
    )

    if args.save:
        save_measurements(
            measurements
        )

        latest_measurement = (
            get_latest_measurement()
        )

        if latest_measurement:
            print_measurement(
                "Latest saved measurement",
                latest_measurement,
            )

    if args.save_sqlite:
        save_sqlite_measurements(
            measurements
        )

        latest_sqlite_measurement = (
            get_latest_sqlite_measurement()
        )

        if latest_sqlite_measurement:
            print_measurement(
                "Latest SQLite measurement",
                latest_sqlite_measurement,
            )

    if args.plot:
        save_plot(
            daylight_dataframe,
            args.plot,
        )

        print(
            f"\nSaved plot to {args.plot}"
        )


if __name__ == "__main__":
    main()
