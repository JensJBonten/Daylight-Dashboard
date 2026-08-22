from __future__ import annotations

from pathlib import Path

import altair as alt
import matplotlib.pyplot as plt
import pandas as pd


def save_plot(
    daylight_dataframe: pd.DataFrame,
    output_path: Path,
) -> None:
    """Lagrer en enkel graf som viser dagslengde og daglig økning."""

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

def build_reference_daylight_chart(
    reference_data: pd.DataFrame,
    measurement_data: pd.DataFrame,
) -> alt.LayerChart:
    """Bygg graf med MET-referanse og egne lagrede målinger."""

    reference_chart = (
        alt.Chart(reference_data)
        .mark_line(
            opacity=0.30,
            strokeWidth=2,
            color="#6B7280",
        )
        .encode(
            x=alt.X(
                "date:T",
                title="Dato",
            ),
            y=alt.Y(
                "daylight_hours:Q",
                title="Dagslys (timer)",
                scale=alt.Scale(
                    zero=False,
                ),
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
                size=110,
            ),
            strokeWidth=3,
            color="#2E7D32",
        )
        .encode(
            x=alt.X(
                "date:T",
                title="Dato",
            ),
            y=alt.Y(
                "Dagslengde (timer):Q",
                title="Dagslys (timer)",
                scale=alt.Scale(
                    zero=False,
                ),
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

    chart = (
        alt.layer(
            reference_chart,
            measurement_chart,
        )
        .properties(
            height=360,
        )
        .interactive()
        .configure(
            background="transparent",
        )
        .configure_view(
            strokeOpacity=0,
        )
    )

    return chart