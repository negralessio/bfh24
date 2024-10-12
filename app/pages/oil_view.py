import streamlit as st
from streamlit_extras.grid import grid
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt


# Charts
def create_fuel_gauge(fuel_level, max_fuel_level, min_value=0, max_value=None):
    """
    Creates a gauge chart for fuel levels in liters.

    Parameters:
    - fuel_level (int or float): Current fuel level in liters.
    - max_fuel_level (int or float): Maximum fuel capacity in liters.
    - min_value (int or float): Minimum value for the gauge.
    - max_value (int or float): Maximum value for the gauge. If None, defaults to max_fuel_level.

    Returns:
    - fig: Plotly figure object.
    """
    if max_value is None:
        max_value = max_fuel_level  # Default max value to max_fuel_level if not specified

    # Create the gauge chart
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=fuel_level,
            title={"text": "Fuel Level (Liters)"},
            gauge={
                "axis": {"range": [min_value, max_value]},
                "bar": {"color": "blue"},
                "steps": [
                    {"range": [min_value, max_value * 0.5], "color": "lightgray"},
                    {"range": [max_value * 0.5, max_value], "color": "orange"},
                ],
                "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": max_value * 0.8},
            },
        )
    )

    # Set the layout to control the size
    fig.update_layout(height=200, width=400)  # Adjust height and width as needed

    return fig


def load_data(file_path: str):
    df = pd.read_pickle(file_path)
    df = df[df["Tank-ID"] != 5]

    # Berechne mindesfüllmenge mit 20%
    df["Warnungsfüllstand"] = df["Maximale Füllgrenze"] * 0.2

    return df


df = load_data("data/processed/data_one_day_clean.pickle")


def view_oil_forecast_page(CFG: dict) -> None:
    # Own Styles
    st.markdown(
        """
        <style>
        .stMetric {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        tank_id = st.selectbox("Select the tank", list(df["Tank-ID"].unique()))
        number_of_days = st.slider(
            "Select number of days",
            min_value=1,
            max_value=len(df[df["Tank-ID"] == tank_id]["Zeitstempel"]),
            value=90,
            step=1,
            help="Show oil consumption of the last n days",
        )

    # Content
    st.header("Dashboard")

    filtered_data = df[(df["Tank-ID"] == tank_id)]

    # Using grid layout for alignment
    my_grid = grid([2, 2], 1, vertical_align="bottom")

    # Row 1:
    with my_grid.container():
        col1, col2 = st.columns(2)  # Create two columns for the first row
        with col1:
            st.metric(
                "Current liters of oil:",
                f"{filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Füllstand'].values[0]}",
            )
        with col2:
            st.metric(
                "Maximum charge:",
                f"{filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Maximale Füllgrenze'].values[0]}",
            )

    # Row 2:
    with my_grid.container():
        col3, col4 = st.columns(2)  # Create two columns for the second row
        with col3:
            st.metric(
                "Need to buy (at a reserve of ):",
                f"{filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Warnungsfüllstand'].values[0]}",
            )

        with col4:
            st.metric("Oil consumption yesterday:", "TBD liters", "0.00")

    # Row 3
    with my_grid.container():
        filtered_data = filtered_data.sort_values("Zeitstempel").tail(number_of_days)
        st.line_chart(
            data=filtered_data,
            x="Zeitstempel",
            y=["Füllstand", "Warnungsfüllstand", "Maximale Füllgrenze"],
            color=["#0000FF", "#FF0000", "#FF0000"],
        )


# Assuming this function is called to render the page
# view_dashboard_page({})
