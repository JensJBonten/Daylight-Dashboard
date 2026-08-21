from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

import src.reference_data as reference_data_module
from src.reference_data import (
    ReferenceDataError,
    load_reference_data,
)


def test_load_reference_data_filters_location(
    tmp_path,
    monkeypatch,
):
    reference_file = (
        tmp_path
        / "reference_daylight_2026.csv"
    )

    pd.DataFrame(
        [
            {
                "location_name": "Oslo",
                "reference_date": "2026-08-10",
                "day_length": "16:14:00",
            },
            {
                "location_name": "Bergen",
                "reference_date": "2026-08-10",
                "day_length": "16:28:00",
            },
        ]
    ).to_csv(
        reference_file,
        index=False,
    )

    monkeypatch.setattr(
        reference_data_module,
        "get_reference_file_path",
        lambda year: reference_file,
    )

    result = load_reference_data(
        "Oslo",
        year=2026,
    )

    assert len(result) == 1
    assert result.iloc[0]["location_name"] == "Oslo"
    assert result.iloc[0]["daylight_hours"] == pytest.approx(
        16 + 14 / 60
    )


def test_load_reference_data_returns_empty_for_unknown_location(
    tmp_path,
    monkeypatch,
):
    reference_file = (
        tmp_path
        / "reference_daylight_2026.csv"
    )

    pd.DataFrame(
        [
            {
                "location_name": "Oslo",
                "reference_date": "2026-08-10",
                "day_length": "16:14:00",
            },
        ]
    ).to_csv(
        reference_file,
        index=False,
    )

    monkeypatch.setattr(
        reference_data_module,
        "get_reference_file_path",
        lambda year: reference_file,
    )

    result = load_reference_data(
        "Tromsø",
        year=2026,
    )

    assert result.empty


def test_load_reference_data_raises_for_missing_file(
    tmp_path,
    monkeypatch,
):
    missing_file = (
        tmp_path
        / "missing.csv"
    )

    monkeypatch.setattr(
        reference_data_module,
        "get_reference_file_path",
        lambda year: missing_file,
    )

    with pytest.raises(
        ReferenceDataError,
        match="Fant ikke referansedata",
    ):
        load_reference_data(
            "Oslo",
            year=date.today().year,
        )