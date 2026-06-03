from __future__ import annotations

from datetime import date

try:
    from .api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from .measurement import DaylightMeasurement
    from .sqlite_storage import save_measurement
except ImportError:
    from api_client import (
        ApiLocation,
        create_measurement_from_sunrise_data,
        fetch_sunrise_data,
    )
    from measurement import DaylightMeasurement
    from sqlite_storage import save_measurement


def fetch_measurement_for_location(location: ApiLocation,measurement_date: date,) -> DaylightMeasurement:
    """Henter MET-data og gjør responsen om til en DaylightMeasuremenet."""
    sunrise_response = fetch_sunrise_data(location, measurement_date)
    # Mapper fra API-respons (JSON) til prosjektet målemetode: 
    measurement = create_measurement_from_sunrise_data(sunrise_response, location)
    
    return measurement

def fetch_and_save_measurement (location: ApiLocation, measurement_date: date) -> DaylightMeasurement:
    """Henter en dagslysmåling fra API og lagrer den i SQlite"""
    
    measurement = fetch_measurement_for_location(location, measurement_date)
    
    # Lagrer enn så lenge med source="API", slik at data fra API og Excell kan skilles.
    save_measurement(measurement, source="api")
    
    return measurement