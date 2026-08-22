from __future__ import annotations

import streamlit as st


def apply_custom_styles() -> None:
    """Tilpasser sidepanelet og bekreftelsesmeldingen."""

    st.markdown(
        """
        <style>
        /* Overskriften "Kontroller" */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            font-size: 1.35rem !important;
            font-weight: 800 !important;
            color: #17324D !important;
        }

        /* Etiketten "Sted" over dropdownen */
        [data-testid="stSidebar"] label p {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #17324D !important;
        }

        /* Forklaringsteksten under dropdownen */
        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            line-height: 1.45 !important;
            color: #17324D !important;
        }

        /* Dropdownen for valg av sted */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background-color: #EAF6FF !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            color: #111827 !important;
            min-height: 44px !important;
        }

        /* Teksten inne i dropdownen */
        [data-testid="stSidebar"] div[data-baseweb="select"] span {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* Innsjekkingsknappen */
        [data-testid="stSidebar"] [data-testid="stButton"] > button {
            width: 100%;
            min-height: 44px;
            background-color: #EAF6FF !important;
            color: #111827 !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        /* Teksten inne i knappen */
        [data-testid="stSidebar"] [data-testid="stButton"] button p {
            font-size: 1rem !important;
            font-weight: 700 !important;
            color: #111827 !important;
        }

        /* Hover-effekt på knappen */
        [data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
            background-color: #D8EEFA !important;
            border-color: #3689B8 !important;
            color: #111827 !important;
        }

        /* Bekreftelsesmeldingen etter lagring */
        .daylight-result-card {
            background-color: #EAF6FF !important;
            color: #111827 !important;
            border: 1px solid #5E9FC4 !important;
            border-radius: 8px !important;
            padding: 12px 14px !important;
            margin: 10px 0 12px 0 !important;
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            line-height: 1.45 !important;
        }

        .daylight-result-card span,
        .daylight-result-card strong {
            color: #111827 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def apply_season_sidebar_style(
    background_color: str,
    accent_color: str,
) -> None:
    """Tilpass sidepanelet til det aktive sesongtemaet."""

    st.markdown(
        f"""
<style>
[data-testid="stSidebar"] {{
    background-color: {background_color} !important;
    border-right-color: {accent_color} !important;
}}
</style>
""",
        unsafe_allow_html=True,
    )