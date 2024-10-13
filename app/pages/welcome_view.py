import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import app.constants.text as text


def view_welcome_page(CFG: dict) -> None:
    st.header(text.SIDEBAR_CONTENT)
    st.markdown(text.WELCOME_TEXT)
