from dataclasses import dataclass


@dataclass
class DaylightMeasurement:
    """Datamodell for en dagslysmåling på ett sted og én dato."""

    # Alle feltene lagres som strenger for at objektet enkelt skal kunne skrives til JSON.
    date: str
    location_name: str
    day_length: str
    sunrise: str
    sunset: str
    daily_increase: str
    total_increase: str

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "location_name": self.location_name,
            "day_length": self.day_length,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "daily_increase": self.daily_increase,
            "total_increase": self.total_increase,
        }

    @classmethod
    def from_dict(cls, measurement_data: dict) -> "DaylightMeasurement":
        return cls(
            date=measurement_data["date"],
            location_name=measurement_data["location_name"],
            day_length=measurement_data["day_length"],
            sunrise=measurement_data["sunrise"],
            sunset=measurement_data["sunset"],
            daily_increase=measurement_data["daily_increase"],
            total_increase=measurement_data["total_increase"],
        )
