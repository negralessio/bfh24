"""
Module handling the streamlit GUI entry point
Run from root via 'python3 -m streamlit app.py'
"""

import streamlit as st
import pandas as pd

import app.constants.text as text
from app.pages.welcome_view import view_welcome_page
from app.pages.oil_view import view_oil_forecast_page
from app.pages.dashboard_view import view_dashboard_page

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

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Welcome"  # Default page

    if st.session_state.selected_page == "Welcome":
        view_welcome_page(CFG)
    elif st.session_state.selected_page == "Indiviudal Dash":
        view_oil_forecast_page(CFG)
    elif st.session_state.selected_page == "Dashboard":
        view_dashboard_page(CFG)


def _render_sidebar() -> None:
    """
    Simply renders and displays the sidebar content.
    """
    button_style = """
        <style>
        .stButton > button {
            width: 100%;  /* Full width */
            font-size: 16px;  /* Button text size */
            padding: 10px;  /* Button padding */
            transition: background-color 0.3s;  /* Smooth transition */
        }

        .stButton > button:hover {
            background-color: #ffeb00;  /* Hover color */
            color: black;  /* Text color on hover */
        }
        </style>
        """

    # Render button styles
    st.sidebar.markdown(button_style, unsafe_allow_html=True)

    with st.sidebar:
        st.image("app/assets/Logo_VEGA_Grieshaber.svg.png")
        st.markdown(text.SIDEBAR_CONTENT)

        if st.sidebar.button("Welcome"):
            st.session_state.selected_page = "Welcome"

        if st.sidebar.button("Dashboard"):
            st.session_state.selected_page = "Dashboard"

        if st.sidebar.button("Indiviudal Dash"):
            st.session_state.selected_page = "Indiviudal Dash"


run_gui()
