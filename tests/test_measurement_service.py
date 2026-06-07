from datetime import date

from src.api_client import ApiLocation
from src.measurement_service import fetch_measurement_for_location
from src.measurement import DaylightMeasurement
from src.measurement_service import add_historical_increase_values


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