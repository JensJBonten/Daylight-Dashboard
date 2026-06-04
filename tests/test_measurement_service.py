from datetime import date

from src.api_client import ApiLocation
from src.measurement_service import fetch_measurement_for_location


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
