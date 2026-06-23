from datetime import date
import sqlite3

import pytest
import requests

from src.api_client import ApiLocation
from src.measurement import DaylightMeasurement
from src.measurement_service import (
    DaylightServiceError,
    add_historical_increase_values,
    fetch_and_save_measurement,
    fetch_measurement_for_location,
)


def test_fetch_measurement_for_location_uses_api_response(monkeypatch):
    """Tester service-laget uten å kalle ekte MET API."""

    fake_response = {
        "properties": {
            "sunrise": {
                "time": "2026-05-27T03:12+01:00",
                "azimuth": 40.81,
            },
            "sunset": {
                "time": "2026-05-27T21:17+01:00",
                "azimuth": 319.56,
            },
        }
    }

    def fake_fetch_sunrise_data(location, measurement_date):
        return fake_response

    monkeypatch.setattr(
        "src.measurement_service.fetch_sunrise_data",
        fake_fetch_sunrise_data,
    )

    location = ApiLocation(name="Grua", latitude=60.257, longitude=10.662)

    measurement = fetch_measurement_for_location(location, date(2026, 5, 27))

    assert measurement.date == "2026-05-27"
    assert measurement.location_name == "Grua"
    assert measurement.day_length == "18:05:00"
    assert measurement.sunrise == "2026-05-27T03:12+01:00"
    assert measurement.sunset == "2026-05-27T21:17+01:00"


def test_add_historical_increase_values_uses_saved_history(monkeypatch):
    """Tester at API-måling får økningstall basert på lagret historikk."""

    api_measurement = DaylightMeasurement(
        date="2026-06-03",
        location_name="Grua",
        day_length="18:29:00",
        sunrise="2026-06-03T03:01+01:00",
        sunset="2026-06-03T21:30+01:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )

    previous_measurement = DaylightMeasurement(
        date="2026-03-10",
        location_name="Grua",
        day_length="11:17:00",
        sunrise="06:49:00",
        sunset="18:06:00",
        daily_increase="00:06:00",
        total_increase="04:08:00",
    )

    first_measurement = DaylightMeasurement(
        date="2026-01-22",
        location_name="Grua",
        day_length="07:09:00",
        sunrise="08:54:00",
        sunset="16:04:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )

    monkeypatch.setattr(
        "src.measurement_service.get_previous_measurement_for_location",
        lambda location_name, measurement_date: previous_measurement,
    )

    monkeypatch.setattr(
        "src.measurement_service.get_first_measurement_for_location",
        lambda location_name: first_measurement,
    )

    measurement = add_historical_increase_values(api_measurement)

    assert measurement.daily_increase == "07:12:00"
    assert measurement.total_increase == "11:20:00"


def test_fetch_and_save_measurement_wraps_api_timeout(monkeypatch):
    """Network errors should become DaylightServiceError."""

    def raise_timeout(location, measurement_date):
        raise requests.Timeout("MET did not respond")

    monkeypatch.setattr(
        "src.measurement_service.fetch_measurement_for_location",
        raise_timeout,
    )

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    with pytest.raises(DaylightServiceError) as error:
        fetch_and_save_measurement(
            location,
            date(2026, 6, 16),
        )

    assert isinstance(error.value.__cause__, requests.Timeout)


def test_fetch_and_save_measurement_wraps_invalid_api_data(monkeypatch):
    """Invalid API data should become DaylightServiceError."""

    invalid_response = {"properties": {"sunrise": {}}}

    monkeypatch.setattr(
        "src.measurement_service.fetch_sunrise_data",
        lambda location, measurement_date: invalid_response,
    )

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    with pytest.raises(DaylightServiceError) as error:
        fetch_and_save_measurement(
            location,
            date(2026, 6, 16),
        )

    assert isinstance(error.value.__cause__, KeyError)


def test_fetch_and_save_measurement_wraps_storage_error(monkeypatch):
    """SQLite errors should become DaylightServiceError."""

    measurement = DaylightMeasurement(
        date="2026-06-16",
        location_name="Grua",
        day_length="18:45:00",
        sunrise="2026-06-16T03:00+02:00",
        sunset="2026-06-16T21:45+02:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )

    monkeypatch.setattr(
        "src.measurement_service.fetch_measurement_for_location",
        lambda location, measurement_date: measurement,
    )

    monkeypatch.setattr(
        "src.measurement_service.add_historical_increase_values",
        lambda saved_measurement: saved_measurement,
    )

    def raise_storage_error(measurement_to_save, source):
        raise sqlite3.OperationalError("Database unavailable")

    monkeypatch.setattr(
        "src.measurement_service.save_measurement",
        raise_storage_error,
    )

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    with pytest.raises(DaylightServiceError) as error:
        fetch_and_save_measurement(
            location,
            date(2026, 6, 16),
        )

    assert isinstance(
        error.value.__cause__,
        sqlite3.OperationalError,
    )


def test_fetch_and_save_measurement_returns_saved_measurement(monkeypatch):
    measurement = DaylightMeasurement(
        date="2026-06-16",
        location_name="Grua",
        day_length="18:45:00",
        sunrise="2026-06-16T03:00+02:00",
        sunset="2026-06-16T21:45+02:00",
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )

    saved_measurement = DaylightMeasurement(
        date="2026-06-16",
        location_name="Grua",
        day_length="18:45:00",
        sunrise="2026-06-16T03:00+02:00",
        sunset="2026-06-16T21:45+02:00",
        daily_increase="00:03:00",
        total_increase="11:20:00",
    )

    saved_calls = []

    monkeypatch.setattr(
        "src.measurement_service.fetch_measurement_for_location",
        lambda location, measurement_date: measurement,
    )
    monkeypatch.setattr(
        "src.measurement_service.add_historical_increase_values",
        lambda api_measurement: saved_measurement,
    )
    monkeypatch.setattr(
        "src.measurement_service.save_measurement",
        lambda measurement_to_save, source: saved_calls.append(
            (measurement_to_save, source)
        ),
    )

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    returned_measurement = fetch_and_save_measurement(
        location,
        date(2026, 6, 16),
    )

    assert returned_measurement == saved_measurement
    assert saved_calls == [(saved_measurement, "api")]
