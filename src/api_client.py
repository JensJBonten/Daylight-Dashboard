from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

import requests

try:
    from .measurement import DaylightMeasurement
except ImportError:
    from measurement import DaylightMeasurement

MET_SUNRISE_URL = "https://api.met.no/weatherapi/sunrise/3.0/sun"


@dataclass
class ApiLocation:
    name: str
    latitude: float
    longitude: float


def get_default_location() -> ApiLocation:
    """Return the project's default API location."""

    return ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )


def get_timezone_offset(measurement_date: date) -> str:
    """Return the Norwegian UTC offset for a date."""

    oslo_datetime = datetime(
        year=measurement_date.year,
        month=measurement_date.month,
        day=measurement_date.day,
        hour=12,
        tzinfo=ZoneInfo("Europe/Oslo"),
    )

    utc_offset = oslo_datetime.utcoffset()

    if utc_offset is None:
        raise ValueError(
            "Could not determine the Norwegian timezone offset."
        )

    total_minutes = int(utc_offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"

    hours, minutes = divmod(abs(total_minutes), 60)

    return f"{sign}{hours:02d}:{minutes:02d}"


def fetch_sunrise_data(location: ApiLocation, measurement_date: date) -> dict:
    """Fetch sunrise and sunset data from the MET Sunrise API."""

    rounded_latitude = round(location.latitude, 4)
    rounded_longitude = round(location.longitude, 4)

    headers = {
        "User-Agent": (
            "DaylightDashboard/1.0 "
            "github.com/JensJBonten/daylight_dashboard"
        ),
        "Accept": "application/json",
    }

    response = requests.get(
        MET_SUNRISE_URL,
        params={
            "lat": rounded_latitude,
            "lon": rounded_longitude,
            "date": measurement_date.isoformat(),
            "offset": get_timezone_offset(measurement_date),
        },
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

    return response.json()


def parse_sunrise_response(sunrise_response: dict) -> dict:
    """Extract sunrise and sunset times from a MET API response."""

    properties = sunrise_response["properties"]
    sunrise_time = properties["sunrise"]["time"]
    sunset_time = properties["sunset"]["time"]

    return {"sunrise": sunrise_time, "sunset": sunset_time}


def calculate_day_length(sunrise_time: str, sunset_time: str) -> str:
    """Calculate day length from ISO-formatted sunrise and sunset times."""

    sunrise_datetime = datetime.fromisoformat(sunrise_time)
    sunset_datetime = datetime.fromisoformat(sunset_time)

    day_length = sunset_datetime - sunrise_datetime

    total_seconds = int(day_length.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def create_measurement_from_sunrise_data(
    sunrise_response: dict,
    location: ApiLocation,
) -> DaylightMeasurement:
    """Build a daylight measurement from a MET API response."""

    sun_times = parse_sunrise_response(sunrise_response)
    sunrise_time = sun_times["sunrise"]
    sunset_time = sun_times["sunset"]
    day_length = calculate_day_length(sunrise_time, sunset_time)

    # The model stores only the date portion of the sunrise timestamp.
    measurement_date = datetime.fromisoformat(sunrise_time).date().isoformat()

    return DaylightMeasurement(
        date=measurement_date,
        location_name=location.name,
        day_length=day_length,
        sunrise=sunrise_time,
        sunset=sunset_time,
        daily_increase="00:00:00",
        total_increase="00:00:00",
    )


def get_api_locations() -> dict[str, ApiLocation]:
    """Return the locations currently supported by the dashboard."""

    return {
        "Grua": ApiLocation(
            name="Grua",
            latitude=60.257,
            longitude=10.662,
        ),
        "Oslo": ApiLocation(
            name="Oslo",
            latitude=59.9139,
            longitude=10.7522,
        ),
        "Tromsø": ApiLocation(
            name="Tromsø",
            latitude=69.6492,
            longitude=18.9553,
        ),
        "Bergen": ApiLocation(
            name="Bergen",
            latitude=60.39299,
            longitude=5.32415,
        ),
    }


def get_api_location_by_name(location_name: str) -> ApiLocation:
    """Return an API location by name."""

    api_locations = get_api_locations()

    if location_name not in api_locations:
        return get_default_location()

    return api_locations[location_name]
