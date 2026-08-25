import pandas as pd

from src.plotting import (
    build_reference_daylight_chart,
)


def test_reference_chart_adds_vertical_headroom():
    reference_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-01-05",
                    "2026-06-22",
                    "2026-12-21",
                ]
            ),
            "daylight_hours": [
                6.0,
                18.8,
                5.9,
            ],
        }
    )

    measurement_data = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-08-25",
                ]
            ),
            "Dagslengde (timer)": [
                14.9,
            ],
        }
    )

    chart = build_reference_daylight_chart(
        reference_data,
        measurement_data,
        "#D9B338",
    )

    chart_specification = chart.to_dict()

    reference_domain = (
        chart_specification[
            "layer"
        ][0][
            "encoding"
        ][
            "y"
        ][
            "scale"
        ][
            "domain"
        ]
    )

    measurement_domain = (
        chart_specification[
            "layer"
        ][1][
            "encoding"
        ][
            "y"
        ][
            "scale"
        ][
            "domain"
        ]
    )

    assert reference_domain[0] < 5.9
    assert reference_domain[1] > 18.8
    assert measurement_domain == reference_domain
    assert chart_specification["padding"]["top"] == 28