from __future__ import annotations

from datetime import date

try:
    from .api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from .measurement import DaylightMeasurement
    from .sqlite_storage import (
        get_first_measurement_for_location,
        get_previous_measurement_for_location,
        save_measurement,
    )
    from .time_utils import calculate_duration_difference
except ImportError:
    from api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from measurement import DaylightMeasurement
    from sqlite_storage import (
        get_first_measurement_for_location,
        get_previous_measurement_for_location,
        save_measurement,
    )
    from time_utils import calculate_duration_difference


def fetch_measurement_for_location(
    location: ApiLocation, measurement_date: date
) -> DaylightMeasurement:
    """Henter MET-data og gjør responsen om til en DaylightMeasurement."""
    sunrise_response = fetch_sunrise_data(location, measurement_date)
    measurement = create_measurement_from_sunrise_data(sunrise_response, location)

    return measurement


def fetch_and_save_measurement(
    location: ApiLocation,
    measurement_date: date,
) -> DaylightMeasurement:
    """Henter API-måling, beregner historikk og lagrer den i SQLite."""

    measurement = fetch_measurement_for_location(location, measurement_date)
    measurement_with_increase = add_historical_increase_values(measurement)

    save_measurement(measurement_with_increase, source="api")

    return measurement_with_increase


def add_historical_increase_values(
    measurement: DaylightMeasurement,
) -> DaylightMeasurement: 
    """Legger til dayly_increase og total_increase basert på lagret historikk."""
    
    previous_measurement = get_previous_measurement_for_location(
        measurement.location_name,
        measurement.date,
    )
    
    first_measurment = get_first_measurement_for_location(
        measurement.location_name,
    )
    
    daily_increase = "00:00:00"
    total_increase = "00:00:00"

    if previous_measurement is not None:
        daily_increase = calculate_duration_difference(
            measurement.day_length,
            previous_measurement.day_length,
        )

    if first_measurment is not None:
        total_increase = calculate_duration_difference(
            measurement.day_length,
            first_measurment.day_length,
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
