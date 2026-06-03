from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from .measurement import DaylightMeasurement

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
    
def calculate_day_length(sunrise_time: str, sunset_time: str) -> str:
    """Funksjonen beregner dagslengde fra soloppgang og solnedgang."""
    
    # MET apiet returnerer ISO-stringer
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
    """Lager en DaylightMeasurement fra MET Sunrise-responsen."""

    parsed_data = parse_sunrise_response(sunrise_response)

    sunrise_time = parsed_data["sunrise"]
    sunset_time = parsed_data["sunset"]

    day_length = calculate_day_length(sunrise_time, sunset_time)

    # Dato hentes fra sunrise-tiden. Vi trenger bare YYYY-MM-DD i modellen.
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



def describe_api_goal() -> list[str]:
    """Beskrivelse av hva API-integrasjonen skal gjøre videre."""

    return [
        "Fetch sunrise and sunset data for a location",
        "Convert API response into DaylightMeasurement objects",
        "Store API measurements in SQLite with source='api'",
        "Show API-backed measurements in the Streamlit dashboard",
    ]