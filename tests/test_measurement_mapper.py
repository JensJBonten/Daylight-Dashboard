import pandas as pd

from src.measurement_mapper import measurements_from_dataframe


def test_measurements_from_dataframe_returns_measurement_list():
    # Bygger et lite DataFrame med samme typer som data_loader returnerer.
    daylight_dataframe = pd.DataFrame(
        [
            {
                "date": pd.Timestamp("2026-01-22"),
                "day_length": pd.Timedelta(hours=7, minutes=9),
                "sunrise": pd.Timedelta(hours=8, minutes=54),
                "sunset": pd.Timedelta(hours=16, minutes=4),
                "change_since_previous_check_in": pd.Timedelta(minutes=0),
                "change_since_first_measurement": pd.Timedelta(minutes=0),
            },
            {
                "date": pd.Timestamp("2026-01-23"),
                "day_length": pd.Timedelta(hours=7, minutes=13),
                "sunrise": pd.Timedelta(hours=8, minutes=52),
                "sunset": pd.Timedelta(hours=16, minutes=6),
                "change_since_previous_check_in": pd.Timedelta(minutes=4),
                "change_since_first_measurement": pd.Timedelta(minutes=4),
            },
        ]
    )

    # Mapper DataFrame-radene til lagringsmodellen og kontrollerer formatet.
    measurements = measurements_from_dataframe(daylight_dataframe, location_name="Grua")

    assert len(measurements) == 2
    assert measurements[0].date == "2026-01-22"
    assert measurements[0].location_name == "Grua"
    assert measurements[0].day_length == "07:09:00"
    assert measurements[1].daily_increase == "00:04:00"
    assert measurements[1].total_increase == "00:04:00"
    assert measurements[1].sunset == "16:06:00"
