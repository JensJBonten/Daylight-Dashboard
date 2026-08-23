from __future__ import annotations

import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from src.api_client import (
    create_measurement_from_sunrise_data,
    fetch_sunrise_data,
    get_api_location_by_name,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REFERENCE_LOCATIONS = (
    "Oslo",
    "Grua",
    "Bergen",
)


def get_latest_monday() -> date:
    """Return the Monday for the current week."""

    today = date.today()

    return today - timedelta(
        days=today.weekday()
    )


def get_weekly_dates(year: int) -> list[date]:
    """Return Mondays from the selected year up to the relevant end date."""

    today = date.today()

    if year > today.year:
        return []

    if year == today.year:
        end_date = get_latest_monday()
    else:
        end_date = date(year, 12, 31)

    weekly_dates = pd.date_range(
        start=f"{year}-01-01",
        end=end_date,
        freq="W-MON",
    )

    return [
        timestamp.date()
        for timestamp in weekly_dates
    ]


def get_output_path(year: int) -> Path:
    """Return the absolute path for the reference CSV."""

    return (
        PROJECT_ROOT
        / "data"
        / f"reference_daylight_{year}.csv"
    )


def load_existing_reference_data(
    year: int,
) -> pd.DataFrame:
    """Load and normalize existing reference data."""

    output_path = get_output_path(year)

    if not output_path.exists():
        return pd.DataFrame()

    existing_data = pd.read_csv(output_path)

    if existing_data.empty:
        return existing_data

    if "reference_date" not in existing_data.columns:
        if "date" not in existing_data.columns:
            raise ValueError(
                f"{output_path} mangler både "
                "'reference_date' og 'date'."
            )

        existing_data["reference_date"] = (
            existing_data["date"]
        )

    required_columns = {
        "location_name",
        "reference_date",
    }

    missing_columns = (
        required_columns
        - set(existing_data.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            f"{output_path} mangler kolonner: "
            f"{missing_text}"
        )

    existing_data["reference_date"] = (
        pd.to_datetime(
            existing_data["reference_date"],
            errors="raise",
        )
        .dt.date
        .astype(str)
    )

    return existing_data


def generate_reference_data(
    year: int,
    existing_data: pd.DataFrame,
) -> pd.DataFrame:
    """Fetch only missing weekly daylight data from MET."""

    weekly_dates = get_weekly_dates(year)

    rows: list[dict] = []

    existing_keys: set[tuple[str, str]] = set()

    if not existing_data.empty:
        existing_keys = set(
            zip(
                existing_data["location_name"],
                existing_data["reference_date"],
            )
        )

    print(
        f"Checking {len(weekly_dates)} weekly points "
        f"per location for {year}."
    )

    for location_name in REFERENCE_LOCATIONS:
        location = get_api_location_by_name(
            location_name
        )

        print(f"\nChecking {location_name}:")

        for measurement_date in weekly_dates:
            date_string = measurement_date.isoformat()

            key = (
                location_name,
                date_string,
            )

            if key in existing_keys:
                print(
                    f"  {date_string} – already stored"
                )
                continue

            print(
                f"  {date_string} – fetching"
            )

            response = fetch_sunrise_data(
                location,
                measurement_date,
            )

            measurement = (
                create_measurement_from_sunrise_data(
                    response,
                    location,
                )
            )

            row = measurement.to_dict()
            row["reference_date"] = date_string

            rows.append(row)

            time.sleep(0.2)

    if rows:
        new_data = pd.DataFrame(rows)

        if existing_data.empty:
            combined_data = new_data
        else:
            combined_data = pd.concat(
                [
                    existing_data,
                    new_data,
                ],
                ignore_index=True,
            )
    else:
        combined_data = existing_data.copy()

    if combined_data.empty:
        return combined_data

    combined_data = (
        combined_data
        .drop_duplicates(
            subset=[
                "location_name",
                "reference_date",
            ],
            keep="last",
        )
        .sort_values(
            [
                "location_name",
                "reference_date",
            ]
        )
        .reset_index(drop=True)
    )

    return combined_data


def save_reference_data(
    reference_data: pd.DataFrame,
    year: int,
) -> Path:
    """Save reference data as CSV."""

    output_path = get_output_path(year)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    reference_data.to_csv(
        output_path,
        index=False,
    )

    return output_path


def main() -> None:
    """Update the current year's reference data."""

    selected_year = date.today().year

    existing_data = load_existing_reference_data(
        selected_year
    )

    reference_data = generate_reference_data(
        selected_year,
        existing_data,
    )

    output_path = save_reference_data(
        reference_data,
        selected_year,
    )

    print()
    print(
        f"Saved {len(reference_data)} rows "
        f"to {output_path}"
    )

    if not reference_data.empty:
        print()
        print("Rows per location:")

        print(
            reference_data.groupby(
                "location_name"
            ).size()
        )


if __name__ == "__main__":
    main()