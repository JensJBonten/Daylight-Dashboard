from src.api_client import get_default_location, describe_api_goal
from src.api_client import parse_sunrise_response


def test_get_default_location_returns_grua():
    """Check that the API client has a default location."""

    location = get_default_location()

    assert location.name == "Grua"
    assert isinstance(location.latitude, float)
    assert isinstance(location.longitude, float)


def test_describe_api_goal_returns_expected_steps():
    """Check that the API integration goal is documented in code."""

    api_goal = describe_api_goal()

    assert "Convert API response into DaylightMeasurement objects" in api_goal
    assert "Store API measurements in SQLite with source='api'" in api_goal


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