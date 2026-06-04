from pathlib import Path
import json

try:
    from .measurement import DaylightMeasurement
except ImportError:
    from measurement import DaylightMeasurement

STORAGE_FILE = Path("data") / "saved_measurements.json"


def load_measurements() -> list[DaylightMeasurement]:
    """Laster alle lagrede målinger fra disk."""
    if not STORAGE_FILE.exists():
        return []

    with open(STORAGE_FILE, "r", encoding="utf-8") as file:
        raw_measurement_data = json.load(file)

    return [
        DaylightMeasurement.from_dict(measurement_data)
        for measurement_data in raw_measurement_data
    ]

def save_measurements(measurements: list[DaylightMeasurement]) -> None:
    """Skriver alle målinger til disk som JSON."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    measurement_records = [measurement.to_dict() for measurement in measurements]

    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(measurement_records, file, indent=4)


def get_latest_measurement() -> DaylightMeasurement | None:
    """Returnerer den sist lagrede målingen hvis det finnes noen."""
    measurements = load_measurements()
    if not measurements:
        return None
    return measurements[-1]
