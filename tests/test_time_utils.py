from datetime import timedelta

from src.time_utils import (
    calculate_duration_difference,
    format_timedelta,
    parse_duration,
)


def test_parse_duration_returns_timedelta():
    duration = parse_duration("18:05:00")

    assert duration == timedelta(hours=18, minutes=5)


def test_format_timedelta_returns_hh_mm_ss():
    formatted_duration = format_timedelta(timedelta(hours=4, minutes=8))

    assert formatted_duration == "04:08:00"


def test_calculate_duration_difference_returns_difference():
    difference = calculate_duration_difference("18:05:00", "11:17:00")

    assert difference == "06:48:00"


def test_format_timedelta_handles_negative_duration():
    formatted_duration = format_timedelta(
        timedelta(minutes=-4)
    )

    assert formatted_duration == "-00:04:00"


def test_calculate_duration_difference_handles_decreasing_daylight():
    difference = calculate_duration_difference(
        "18:01:00",
        "18:05:00",
    )

    assert difference == "-00:04:00"
