import pandas as pd

from src.formatting import format_duration, format_time_for_display


def test_format_duration_formats_timedelta_as_hh_mm_ss():
    formatted_duration = format_duration(pd.Timedelta(hours=4, minutes=8))

    assert formatted_duration == "04:08:00"


def test_format_duration_returns_na_for_missing_value():
    formatted_duration = format_duration(pd.NaT)

    assert formatted_duration == "N/A"


def test_format_time_for_display_handles_met_iso_time():
    formatted_time = format_time_for_display("2026-06-03T03:01+01:00")

    assert formatted_time == "03:01"


def test_format_time_for_display_handles_normal_time_string():
    formatted_time = format_time_for_display("08:54:00")

    assert formatted_time == "08:54"