"""
Module handling the streamlit GUI entry point
Run from root via 'python3 -m streamlit app.py'
"""

import streamlit as st
import pandas as pd

import app.constants.text as text
from app.pages.welcome_view import view_welcome_page
from app.pages.oil_view import view_oil_forecast_page

from src.utils.logger import setup_logger
from src.utils.config_manager import ConfigManager

logger = setup_logger(__name__)

# Load configuration file
CFG_MNG = ConfigManager()
CFG: dict = CFG_MNG.config
# Set page config
st.set_page_config(page_title="Challenge 4: Vega Nachkaufoptimierung", layout="wide", page_icon="📈")


def run_gui() -> None:
    """Entry point of the streamlit GUI"""
    _render_sidebar()

    tab1, tab2, tab3 = st.tabs(
        [
            "Welcome",
            "Oil Price Forecast",
            "Dummy Tab 2",
        ]
    )

    with tab1:
        view_welcome_page(CFG)
    with tab2:
        view_oil_forecast_page(CFG)
    with tab3:
        pass


def _render_sidebar() -> None:
    """
    Simply renders and displays the sidebar content.
    """
    with st.sidebar:
        st.image("app/assets/Logo_VEGA_Grieshaber.svg.png")
        st.markdown(text.SIDEBAR_CONTENT)


run_gui()
