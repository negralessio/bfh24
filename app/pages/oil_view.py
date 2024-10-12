import streamlit as st
from streamlit_extras.grid import grid
import plotly.graph_objects as go


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

    # Content
    st.header("Dashboard")

    # Using grid layout for alignment
    my_grid = grid([2, 2], 1, vertical_align="bottom")

    # Row 1:
    with my_grid.container():
        col1, col2 = st.columns(2)  # Create two columns for the first row
        with col1:
            st.metric("Total Sensors:", "0.00 Euro", "0.00")
        with col2:
            st.metric("Total Heating Oil:", "0.00 Euro", "0.00")

    # Row 2:
    with my_grid.container():
        col3, col4 = st.columns(2)  # Create two columns for the second row
        with col3:
            # Gauge Chart
            gauge_fig = create_fuel_gauge(50, 100)  # Create the gauge chart
            st.plotly_chart(gauge_fig, use_container_width=True)  # Display the gauge chart

        with col4:
            st.metric("Current Heating Oil Price:", "0.00 Euro", "0.00")


# Assuming this function is called to render the page
# view_dashboard_page({})
