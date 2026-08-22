from __future__ import annotations

import sqlite3
from datetime import date

import requests

try:
    from .api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from .measurement import DaylightMeasurement
    from .sqlite_storage import (
        get_first_measurement_for_location,
        get_latest_check_in_measurement,
        save_check_in,
        save_measurement,
    )
    from .time_utils import (
        calculate_duration_difference,
    )

except ImportError:
    from api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from measurement import DaylightMeasurement
    from sqlite_storage import (
        get_first_measurement_for_location,
        get_latest_check_in_measurement,
        save_check_in,
        save_measurement,
    )
    from time_utils import (
        calculate_duration_difference,
    )


class DaylightServiceError(Exception):
    """Raised when daylight data cannot be fetched, processed, or saved."""


EXPECTED_SERVICE_ERRORS = (
    requests.RequestException,
    sqlite3.Error,
    KeyError,
    TypeError,
    ValueError,
)


def fetch_measurement_for_location(
    location: ApiLocation, measurement_date: date
) -> DaylightMeasurement:
    """Fetch MET data and convert it to a daylight measurement."""

    sunrise_response = fetch_sunrise_data(location, measurement_date)
    measurement = create_measurement_from_sunrise_data(sunrise_response, location)

    return measurement


def fetch_and_save_measurement(
    location: ApiLocation,
    measurement_date: date,
) -> DaylightMeasurement:
    """Fetch, process, and save one daylight measurement."""

    try:
        measurement = fetch_measurement_for_location(
            location,
            measurement_date,
        )

        measurement_with_increase = add_historical_increase_values(measurement)

        save_measurement(
            measurement_with_increase,
            source="api",
        )
        save_check_in(
            location_name=measurement_with_increase.location_name,
            check_in_date=measurement_with_increase.date
        )
        
        return measurement_with_increase

    except EXPECTED_SERVICE_ERRORS as error:
        raise DaylightServiceError(
            "Could not fetch or save daylight data."
        ) from error


def add_historical_increase_values(
    measurement: DaylightMeasurement,
) -> DaylightMeasurement:
    """Add daily and total increase values from saved history."""

    previous_measurement = get_latest_check_in_measurement(
        location_name=measurement.location_name,
        before_date=measurement.date,
    )
    first_measurement = get_first_measurement_for_location(
        measurement.location_name,
    )

    daily_increase = "00:00:00"
    total_increase = "00:00:00"

    if previous_measurement is not None:
        daily_increase = calculate_duration_difference(
            measurement.day_length,
            previous_measurement.day_length,
        )

    if first_measurement is not None:
        total_increase = calculate_duration_difference(
            measurement.day_length,
            first_measurement.day_length,
        )

    return DaylightMeasurement(
        date=measurement.date,
        location_name=measurement.location_name,
        day_length=measurement.day_length,
        sunrise=measurement.sunrise,
        sunset=measurement.sunset,
        daily_increase=daily_increase,
        total_increase=total_increase,
    )
