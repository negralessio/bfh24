import numpy as np
import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import app.constants.text as text


def view_welcome_page(CFG: dict) -> None:
    st.header(text.SIDEBAR_CONTENT)
    st.markdown(
        """
    Die VEGA Grieshaber KG bietet Kunden eine innovative Lösung zur Überwachung und Prognose ihrer Lagerbestände an, was rechtzeitige Nachbestellungen ermöglicht. Kann der Nachkaufzeitpunkt für Lagerbestände durch aktuelle, individuelle Einspeisung von Preis-, Chargen- und Materialinformationen optimiert werden? Diese optimalen Nachkaufzeitpunkte sollen unter Berücksichtigung des prognostizierten Füllstandes, Preis (-prognosen) aus öffentlichen oder privaten Preisinformationen ermittelt werden. Als besondere Herausforderung ist zu sehen, dass die Daten zwischen verschiedenen Kunden nicht geteilt werden dürfen.
    """
    )
