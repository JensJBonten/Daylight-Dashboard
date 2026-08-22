from pathlib import Path
import json

try:
    from .measurement import DaylightMeasurement
except ImportError:
    from measurement import DaylightMeasurement

STORAGE_FILE = Path("data") / "saved_measurements.json"


def load_measurements() -> list[DaylightMeasurement]:
    """Load all saved measurements from disk."""
    if not STORAGE_FILE.exists():
        return []

    with open(STORAGE_FILE, "r", encoding="utf-8") as file:
        raw_measurement_data = json.load(file)

    return [
        DaylightMeasurement.from_dict(measurement_data)
        for measurement_data in raw_measurement_data
    ]


def save_measurements(measurements: list[DaylightMeasurement]) -> None:
    """Write all measurements to disk as JSON."""
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    measurement_records = [
        measurement.to_dict()
        for measurement in measurements
    ]

    with open(STORAGE_FILE, "w", encoding="utf-8") as file:
        json.dump(measurement_records, file, indent=4)


def get_latest_measurement() -> DaylightMeasurement | None:
    """Return the latest saved measurement, if one exists."""
    measurements = load_measurements()
    if not measurements:
        return None
    return measurements[-1]
