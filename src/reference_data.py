from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ReferenceDataError(RuntimeError):
    """Raised when reference daylight data cannot be loaded."""


def get_reference_file_path(
    year: int,
) -> Path:
    """Return the reference CSV path for one year."""

    return (
        PROJECT_ROOT
        / "data"
        / f"reference_daylight_{year}.csv"
    )


def load_reference_data(
    location_name: str,
    year: int | None = None,
) -> pd.DataFrame:
    """Load weekly daylight reference data for one location."""

    selected_year = year or date.today().year

    file_path = get_reference_file_path(
        selected_year
    )

    if not file_path.exists():
        raise ReferenceDataError(
            f"Fant ikke referansedata: {file_path}. "
            "Kjør python -m "
            "scripts.generate_reference_data først."
        )

    try:
        reference_data = pd.read_csv(
            file_path
        )
    except (
        OSError,
        pd.errors.EmptyDataError,
    ) as error:
        raise ReferenceDataError(
            f"Kunne ikke lese referansedata fra "
            f"{file_path}."
        ) from error

    if reference_data.empty:
        raise ReferenceDataError(
            f"Referansefilen {file_path} er tom."
        )

    if "reference_date" not in reference_data.columns:
        if "date" not in reference_data.columns:
            raise ReferenceDataError(
                "Referansedata mangler både "
                "'reference_date' og 'date'."
            )

        reference_data["reference_date"] = (
            reference_data["date"]
        )

    required_columns = {
        "location_name",
        "reference_date",
        "day_length",
    }

    missing_columns = (
        required_columns
        - set(reference_data.columns)
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )

        raise ReferenceDataError(
            "Referansedata mangler kolonnene: "
            f"{missing_text}"
        )

    try:
        reference_data["reference_date"] = (
            pd.to_datetime(
                reference_data["reference_date"],
                errors="raise",
            )
        )

        reference_data["daylight_hours"] = (
            pd.to_timedelta(
                reference_data["day_length"],
                errors="raise",
            )
            .dt.total_seconds()
            / 3600
        )
    except (TypeError, ValueError) as error:
        raise ReferenceDataError(
            "Referansedata inneholder ugyldige "
            "datoer eller dagslengder."
        ) from error

    filtered_data = reference_data[
        reference_data["location_name"]
        == location_name
    ].copy()

    filtered_data["date"] = (
        filtered_data["reference_date"]
    )

    return (
        filtered_data
        .sort_values("date")
        .reset_index(drop=True)
    )