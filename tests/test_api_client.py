from datetime import date

import pytest

from src.api_client import (
    ApiLocation,
    calculate_day_length,
    create_measurement_from_sunrise_data,
    fetch_sunrise_data,
    get_api_location_by_name,
    get_default_location,
    get_timezone_offset,
    parse_sunrise_response,
)


def test_get_default_location_returns_grua():
    """Check that the API client has a default location."""

    location = get_default_location()

    assert location.name == "Grua"
    assert isinstance(location.latitude, float)
    assert isinstance(location.longitude, float)


def test_parse_sunrise_response_extracts_sunrise_and_sunset():
    """Tester at MET Sunrise-responsen parses til verdiene vi trenger."""

    sunrise_response = {
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

    parsed_data = parse_sunrise_response(sunrise_response)
    assert parsed_data["sunrise"] == "2026-05-27T03:12+01:00"
    assert parsed_data["sunset"] == "2026-05-27T21:17+01:00"


def test_calculate_day_length_returns_duration_between_sunrise_and_sunset():
    """Tester at dagslengde beregnes fra soloppgang og solnedgang."""

    day_length = calculate_day_length(
        "2026-05-27T03:12+01:00",
        "2026-05-27T21:17+01:00",
    )

    assert day_length == "18:05:00"


def test_create_measurement_from_sunrise_data_returns_daylight_measurement():
    """Tester at MET Sunrise-data kan gjøres om til DaylightMeasurement."""

    sunrise_response = {
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

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    measurement = create_measurement_from_sunrise_data(sunrise_response, location)
    assert measurement.date == "2026-05-27"
    assert measurement.location_name == "Grua"
    assert measurement.day_length == "18:05:00"
    assert measurement.sunrise == "2026-05-27T03:12+01:00"
    assert measurement.sunset == "2026-05-27T21:17+01:00"


def test_get_api_location_by_name_returns_grua():
    location = get_api_location_by_name("Grua")

    assert location.name == "Grua"
    assert location.latitude == 60.257
    assert location.longitude == 10.662


def test_get_timezone_offset_returns_winter_offset():
    offset = get_timezone_offset(date(2026, 1, 15))

    assert offset == "+01:00"


def test_get_timezone_offset_returns_summer_offset():
    offset = get_timezone_offset(date(2026, 7, 15))

    assert offset == "+02:00"


@pytest.mark.parametrize(
    ("measurement_date", "expected_offset"),
    [
        (date(2026, 1, 15), "+01:00"),
        (date(2026, 7, 15), "+02:00"),
    ],
)
def test_fetch_sunrise_data_uses_oslo_timezone_offset(
    monkeypatch,
    measurement_date,
    expected_offset,
):
    captured_request = {}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"properties": {}}

    def fake_get(url, params, headers, timeout):
        captured_request["params"] = params
        captured_request["headers"] = headers

        return FakeResponse()

    monkeypatch.setattr(
        "src.api_client.requests.get",
        fake_get,
    )

    location = ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )

    fetch_sunrise_data(
        location,
        measurement_date,
    )

    assert captured_request["params"]["offset"] == expected_offset
    assert (
        captured_request["headers"]["User-Agent"]
        == "DaylightDashboard/1.0 github.com/JensJBonten/daylight_dashboard"
    )
