from __future__ import annotations

from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd

try:
    from .seasonal import get_solstices
except ImportError:
    from seasonal import get_solstices


AXIS_LABEL_COLOR = "#64748B"
AXIS_TITLE_COLOR = "#17324D"
AXIS_GRID_COLOR = "#E7EDF3"
AXIS_DOMAIN_COLOR = "#CBD5E1"
REFERENCE_COLOR = "#94A3B8"


def save_plot(
    daylight_dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Save a chart showing day length and daily increase."""

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(11, 8),
        sharex=True,
    )

    axes[0].plot(
        daylight_dataframe["date"],
        daylight_dataframe[
            "day_length"
        ].dt.total_seconds()
        / 3600,
        linewidth=2,
    )

    axes[0].set_title(
        "Day Length Over Time"
    )
    axes[0].set_ylabel("Hours")
    axes[0].grid(alpha=0.3)

    axes[1].bar(
        daylight_dataframe["date"],
        daylight_dataframe[
            "daily_increase"
        ].dt.total_seconds()
        / 60,
        width=1.5,
    )

    axes[1].set_title(
        "Daily Increase"
    )
    axes[1].set_ylabel("Minutes")
    axes[1].grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=150,
    )

    plt.close(fig)


def _build_daylight_y_scale(
    reference_data: pd.DataFrame,
    measurement_data: pd.DataFrame,
) -> alt.Scale:
    """Build a shared Y scale with visible space around the data."""

    daylight_values = [
        reference_data["daylight_hours"]
    ]

    if not measurement_data.empty:
        daylight_values.append(
            measurement_data[
                "Dagslengde (timer)"
            ]
        )

    combined_values = pd.concat(
        daylight_values,
        ignore_index=True,
    ).dropna()

    if combined_values.empty:
        return alt.Scale(
            zero=False,
        )

    minimum_value = float(
        combined_values.min()
    )

    maximum_value = float(
        combined_values.max()
    )

    value_range = (
        maximum_value
        - minimum_value
    )

    padding = max(
        value_range * 0.08,
        0.5,
    )

    return alt.Scale(
        domain=[
            max(
                0.0,
                minimum_value - padding,
            ),
            maximum_value + padding,
        ],
        zero=False,
        nice=False,
    )


def build_reference_daylight_chart(
    reference_data: pd.DataFrame,
    measurement_data: pd.DataFrame,
    accent_color: str,
) -> alt.LayerChart:
    """Build the annual daylight reference chart."""

    selected_year = int(
        reference_data[
            "date"
        ].dt.year.iloc[0]
    )

    (
        summer_solstice,
        winter_solstice,
    ) = get_solstices(
        selected_year
    )

    summer_timestamp = pd.Timestamp(
        summer_solstice.date
    )

    winter_timestamp = pd.Timestamp(
        winter_solstice.date
    )

    chart_start = (
        reference_data["date"].min()
    )

    chart_end = winter_timestamp

    if not measurement_data.empty:
        measurement_start = (
            measurement_data[
                "date"
            ].min()
        )

        chart_start = min(
            chart_start,
            measurement_start,
        )

    x_scale = alt.Scale(
        domain=[
            chart_start,
            chart_end,
        ]
    )

    y_scale = _build_daylight_y_scale(
        reference_data,
        measurement_data,
    )

    reference_chart = (
        alt.Chart(reference_data)
        .mark_line(
            opacity=0.55,
            strokeWidth=2,
            color=REFERENCE_COLOR,
        )
        .encode(
            x=alt.X(
                "date:T",
                title="Dato",
                scale=x_scale,
                axis=alt.Axis(
                    format="%b",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "daylight_hours:Q",
                title="Dagslys (timer)",
                scale=y_scale,
            ),
            tooltip=[
                alt.Tooltip(
                    "date:T",
                    title="Referansedato",
                    format="%d.%m.%Y",
                ),
                alt.Tooltip(
                    "daylight_hours:Q",
                    title="MET-referanse",
                    format=".2f",
                ),
            ],
        )
    )

    measurement_chart = (
        alt.Chart(measurement_data)
        .transform_calculate(
            Registrering="'Din måling'"
        )
        .mark_line(
            point=alt.OverlayMarkDef(
                filled=True,
                size=105,
                fill=accent_color,
                stroke="#FFFFFF",
                strokeWidth=2,
            ),
            strokeWidth=3,
            color=accent_color,
        )
        .encode(
            x=alt.X(
                "date:T",
                title="Dato",
                scale=x_scale,
                axis=alt.Axis(
                    format="%b",
                    labelAngle=0,
                ),
            ),
            y=alt.Y(
                "Dagslengde (timer):Q",
                title="Dagslys (timer)",
                scale=y_scale,
            ),
            tooltip=[
                alt.Tooltip(
                    "Registrering:N",
                    title="Type",
                ),
                alt.Tooltip(
                    "date:T",
                    title="Dato",
                    format="%d.%m.%Y",
                ),
                alt.Tooltip(
                    "Dagslengde (timer):Q",
                    title="Dagslys",
                    format=".2f",
                ),
            ],
        )
    )

    solstice_data = pd.DataFrame(
        [
            {
                "date": summer_timestamp,
                "label": (
                    f"{summer_solstice.icon} "
                    f"{summer_solstice.name}"
                ),
            },
            {
                "date": winter_timestamp,
                "label": (
                    f"{winter_solstice.icon} "
                    f"{winter_solstice.name}"
                ),
            },
        ]
    )

    solstice_rules = (
        alt.Chart(solstice_data)
        .mark_rule(
            strokeDash=[5, 5],
            strokeWidth=1.5,
            opacity=0.7,
            color=REFERENCE_COLOR,
        )
        .encode(
            x=alt.X(
                "date:T",
                scale=x_scale,
            ),
            tooltip=[
                alt.Tooltip(
                    "label:N",
                    title="Solverv",
                ),
                alt.Tooltip(
                    "date:T",
                    title="Dato",
                    format="%d.%m.%Y",
                ),
            ],
        )
    )

    solstice_labels = (
        alt.Chart(solstice_data)
        .mark_text(
            angle=270,
            align="left",
            baseline="middle",
            color=AXIS_LABEL_COLOR,
            fontSize=11,
            fontWeight=600,
        )
        .encode(
            x=alt.X(
                "date:T",
                scale=x_scale,
            ),
            y=alt.value(16),
            text=alt.Text(
                "label:N",
            ),
        )
    )

    chart = (
        alt.layer(
            reference_chart,
            measurement_chart,
            solstice_rules,
            solstice_labels,
        )
        .properties(
            height=360,
            padding={
                "top": 28,
                "right": 18,
                "bottom": 12,
                "left": 8,
            },
        )
        .interactive()
        .configure(
            background="transparent",
        )
        .configure_axis(
            labelColor=AXIS_LABEL_COLOR,
            labelFontSize=11,
            labelPadding=8,
            titleColor=AXIS_TITLE_COLOR,
            titleFontSize=12,
            titleFontWeight=600,
            titlePadding=14,
            gridColor=AXIS_GRID_COLOR,
            gridOpacity=0.8,
            domainColor=AXIS_DOMAIN_COLOR,
            tickColor=AXIS_DOMAIN_COLOR,
        )
        .configure_view(
            strokeOpacity=0,
        )
    )

    return chart


def build_measurement_change_chart(
    measurements_dataframe: pd.DataFrame,
    accent_color: str,
) -> alt.LayerChart:
    """Build a chart showing change between saved measurements."""

    chart_data = (
        measurements_dataframe[
            [
                "date",
                "Endring siden sist (minutter)",
            ]
        ]
        .dropna()
        .copy()
    )

    bars = (
        alt.Chart(chart_data)
        .mark_bar(
            color=accent_color,
            opacity=0.9,
            cornerRadius=4,
        )
        .encode(
            x=alt.X(
                "date:T",
                title="Dato",
                axis=alt.Axis(
                    format="%d.%m",
                    labelAngle=0,
                    labelOverlap="greedy",
                ),
            ),
            y=alt.Y(
                "Endring siden sist (minutter):Q",
                title="Endring (minutter)",
            ),
            tooltip=[
                alt.Tooltip(
                    "date:T",
                    title="Dato",
                    format="%d.%m.%Y",
                ),
                alt.Tooltip(
                    "Endring siden sist (minutter):Q",
                    title="Endring",
                    format=".1f",
                ),
            ],
        )
    )

    zero_line = (
        alt.Chart(
            pd.DataFrame(
                {
                    "zero": [0],
                }
            )
        )
        .mark_rule(
            color=AXIS_DOMAIN_COLOR,
            strokeWidth=1,
        )
        .encode(
            y="zero:Q",
        )
    )

    chart = (
        alt.layer(
            bars,
            zero_line,
        )
        .properties(
            height=300,
            padding={
                "top": 14,
                "right": 18,
                "bottom": 12,
                "left": 8,
            },
        )
        .configure(
            background="transparent",
        )
        .configure_axis(
            labelColor=AXIS_LABEL_COLOR,
            labelFontSize=11,
            labelPadding=8,
            titleColor=AXIS_TITLE_COLOR,
            titleFontSize=12,
            titleFontWeight=600,
            titlePadding=14,
            gridColor=AXIS_GRID_COLOR,
            gridOpacity=0.8,
            domainColor=AXIS_DOMAIN_COLOR,
            tickColor=AXIS_DOMAIN_COLOR,
        )
        .configure_view(
            strokeOpacity=0,
        )
    )

    return chart