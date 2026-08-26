from __future__ import annotations

from pathlib import Path

import streamlit as st


STYLES_PATH = (
    Path(__file__).resolve().parent
    / "styles"
    / "dashboard.css"
)


def apply_custom_styles() -> None:
    """Apply custom styles to the dashboard."""

    css = STYLES_PATH.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


def apply_season_sidebar_style(
    background_color: str,
    accent_color: str,
) -> None:
    """Apply seasonal accents without recoloring the whole sidebar."""

    st.markdown(
        f"""
<style>
:root {{
    --dd-season-background: {background_color};
    --dd-season-accent: {accent_color};
}}

[data-testid="stSidebar"] {{
    background:
        var(--dd-surface-muted) !important;

    border-right:
        3px solid
        var(--dd-season-accent) !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )
