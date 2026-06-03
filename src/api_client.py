from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import requests


MET_SUNRISE_URL = "https://api.met.no/weatherapi/sunrise/3.0/sun"


@dataclass
class ApiLocation:
    name: str
    latitude: float
    longitude: float


def get_default_location() -> ApiLocation:
    """Returnerer default-lokasjonen som brukes i prosjektet."""

    return ApiLocation(
        name="Grua",
        latitude=60.257,
        longitude=10.662,
    )


def fetch_sunrise_data(location: ApiLocation, measurement_date: date) -> dict:
    """Henter soloppgang og solnedgang fra MET Sunrise API."""

    rounded_latitude = round(location.latitude, 4)
    rounded_longitude = round(location.longitude, 4)

    headers = {
        "User-Agent": "DaylightDashboard/0.1 github.com/JensBonten/daylight-dashboard",
        "Accept": "application/json",
    }

    response = requests.get(
        MET_SUNRISE_URL,
        params={
            "lat": rounded_latitude,
            "lon": rounded_longitude,
            "date": measurement_date.isoformat(),
            # Norge er UTC+01 om vinteren og UTC+02 om sommeren.
            # Dette settes hardkodet nå og forbedres senere.
            "offset": "+01:00",
        },
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()

    return response.json()

def parse_sunrise_response(sunrise_response: dict) -> dict:
    """Henter ut soloppgang og solnedgang fra MET Sunrise-responsen."""

    properties = sunrise_response["properties"]

    sunrise_time = properties["sunrise"]["time"]
    sunset_time = properties["sunset"]["time"]

    return {
        "sunrise": sunrise_time,
        "sunset": sunset_time,
    }


def describe_api_goal() -> list[str]:
    """Beskrivelse av hva API-integrasjonen skal gjøre videre."""

    return [
        "Fetch sunrise and sunset data for a location",
        "Convert API response into DaylightMeasurement objects",
        "Store API measurements in SQLite with source='api'",
        "Show API-backed measurements in the Streamlit dashboard",
    ]