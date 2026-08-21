from __future__ import annotations

from datetime import date

import pandas as pd

from scripts.generate_reference_data import (
    REFERENCE_LOCATIONS,
    generate_reference_data,
    get_latest_monday,
    get_weekly_dates,
)


def test_current_year_stops_at_latest_monday():
    weekly_dates = get_weekly_dates(
        date.today().year
    )

    assert weekly_dates
    assert weekly_dates[-1] == get_latest_monday()
    assert all(
        weekly_date.weekday() == 0
        for weekly_date in weekly_dates
    )
    assert all(
        weekly_date <= date.today()
        for weekly_date in weekly_dates
    )


def test_existing_weekly_data_is_not_fetched_again(
    monkeypatch,
):
    year = date.today().year
    weekly_dates = get_weekly_dates(year)

    existing_rows = [
        {
            "location_name": location_name,
            "reference_date": weekly_date.isoformat(),
        }
        for location_name in REFERENCE_LOCATIONS
        for weekly_date in weekly_dates
    ]

    existing_data = pd.DataFrame(
        existing_rows
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError(
            "MET should not be called for "
            "existing reference data."
        )

    monkeypatch.setattr(
        "scripts.generate_reference_data."
        "fetch_sunrise_data",
        fail_if_called,
    )

    result = generate_reference_data(
        year,
        existing_data,
    )

    assert len(result) == len(existing_data)