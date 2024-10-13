import streamlit as st
from streamlit_extras.grid import grid
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from datetime import datetime

from src.forcasting import run_oil_consumption_forecasting, get_cleaned_data, fit_linear_model


# Charts

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
            "Select number of historical days",
            min_value=1,
            max_value=len(df[df["Tank-ID"] == tank_id]["Zeitstempel"]),
            value=90,
            step=1,
            help="Show oil consumption of the last n days",
        )

        number_of_forecast = st.slider(
            "Select number of days to forecast",
            min_value=1,
            max_value=30,
            value=14,
            step=1,
            help="Number of days to forecast the oil consumption",
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
            current_liters = filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Füllstand'].values[0]
            one_week_before = filtered_data.sort_values('Zeitstempel', ascending=False).head(7).tail(1)['Füllstand'].values[0]
            st.metric(
                "Current liters of oil:",
                f"{current_liters} liters",
                f"One week before: {one_week_before} liters"
            )
        with col2:
            st.metric(
                "Maximum charge:",
                f"{filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Maximale Füllgrenze'].values[0]} liters",
            )

    # Row 2:
    with my_grid.container():
        col3, col4 = st.columns(2)  # Create two columns for the second row
        with col3:
            reserve = filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Warnungsfüllstand'].values[0]
            current_liters = filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Füllstand'].values[0]

            clean_data = get_cleaned_data()
            y_train, y_pred, y_pred_future = fit_linear_model(df=clean_data, context=2, forecast_days=10000)

             # Convert timestamps
            y_train["Zeitstempel"] = y_train["Zeitstempel"].astype("datetime64[ns]")
            y_pred["Zeitstempel"] = y_pred["Zeitstempel"].astype("datetime64[ns]")
            y_pred_future["Zeitstempel"] = y_pred_future["Zeitstempel"].astype("datetime64[ns]")
            filtered_data["Zeitstempel"] = filtered_data["Zeitstempel"].astype("datetime64[ns]")

            # Add Füllstand
            y_train = y_train.merge(filtered_data[["Zeitstempel", "Füllstand"]], left_on=["Zeitstempel"], right_on=["Zeitstempel"], how="left")
            y_pred_future["Füllstand"] = current_liters
            y_pred_future["Verbrauch kummuliert"] = y_pred_future['Verbrauch'].cumsum()
            y_pred_future["Füllstand"] = y_pred_future["Füllstand"] - y_pred_future["Verbrauch kummuliert"]
            y_pred_future["Prognostizierter Füllstand"] = y_pred_future["Füllstand"]
            y_pred_future.drop("Füllstand", axis=1, inplace=True)

            consumption_mean = filtered_data.sort_values('Zeitstempel', ascending=False).head(5)['Verbrauch'].sum() / 5
            #prog_days = int(np.abs(current_liters / consumption_mean))

            reserve_kauf = y_pred_future[y_pred_future["Prognostizierter Füllstand"] < reserve].head(1)["Zeitstempel"].values[0]
            today = datetime.today()
            # Differenz in Tagen berechnen
            #days_difference = (today - datetime((reserve_kauf))).days
            reserve_kauf = str(reserve_kauf).split('T')[0]

            leer_kauf = y_pred_future[y_pred_future["Prognostizierter Füllstand"] < 0].head().values[0]

            st.metric(
                "Need to buy (at a reserve of 20%):",
                f"{reserve} liters\n",
                f"on {reserve_kauf}"
            )

        with col4:
            consumption_yesterday = filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Verbrauch'].values[0]
            consumption_yesterday_2 = filtered_data.sort_values('Zeitstempel', ascending=False).head(2).tail(1)['Verbrauch'].values[0]
            st.metric("Oil consumption yesterday:", 
                      f"{np.abs(consumption_yesterday)}",
                      f"{np.abs(consumption_yesterday_2 - consumption_yesterday)}",)

    # Row 3
    with my_grid.container():
        current_liters = filtered_data.sort_values('Zeitstempel', ascending=False).head(1)['Füllstand'].values[0]
        filtered_data = filtered_data.sort_values("Zeitstempel").tail(number_of_days)
        # st.line_chart(
        #     data=filtered_data,
        #     x="Zeitstempel",
        #     y=["Füllstand", "Warnungsfüllstand", "Maximale Füllgrenze"],
        #     color=["#0000FF", "#FF0000", "#FF0000"],
        # )

        clean_data = get_cleaned_data()
        y_train, y_pred, y_pred_future = fit_linear_model(df=clean_data, context=number_of_days, forecast_days=number_of_forecast, degree=1)

        # Convert timestamps
        y_train["Zeitstempel"] = y_train["Zeitstempel"].astype("datetime64[ns]")
        y_pred["Zeitstempel"] = y_pred["Zeitstempel"].astype("datetime64[ns]")
        y_pred_future["Zeitstempel"] = y_pred_future["Zeitstempel"].astype("datetime64[ns]")
        filtered_data["Zeitstempel"] = filtered_data["Zeitstempel"].astype("datetime64[ns]")

        # Add Füllstand
        y_train = y_train.merge(filtered_data[["Zeitstempel", "Füllstand"]], left_on=["Zeitstempel"], right_on=["Zeitstempel"], how="left")
        y_pred_future["Füllstand"] = current_liters
        y_pred_future["Füllstand"] = y_pred_future["Füllstand"] - y_pred_future["Verbrauch"]
        y_pred_future["Prognostizierter Füllstand"] = y_pred_future["Füllstand"]
        y_pred_future.drop("Füllstand", axis=1, inplace=True)

        # Füllstand
        # Is_pred

        df_plot = pd.concat([y_train, y_pred_future], axis=0, ignore_index=True)
        df_plot = df_plot.merge(filtered_data[["Zeitstempel", "Warnungsfüllstand", "Maximale Füllgrenze"]], how="left", left_on=["Zeitstempel"], right_on=["Zeitstempel"])

        st.line_chart(
            data=df_plot,
            x="Zeitstempel",
            y=["Prognostizierter Füllstand", "Füllstand", "Warnungsfüllstand", "Maximale Füllgrenze"],
            color=["#000000", "#FF0000", "#0000FF", "#FF0000"],
        )

# Assuming this function is called to render the page
# view_dashboard_page({})
