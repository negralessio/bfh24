import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
from src.api import OilPriceAPI, WeatherAPI
from datetime import datetime, timedelta
import folium
import plotly.express as px


def load_data(file_path: str) -> pd.DataFrame:
    # Load data from the specified file
    data = pd.read_pickle(file_path)
    print(data.head())

    # Remove all rows where Tank-ID = 5
    data = data[data["Tank-ID"] != 5]

    # Convert PLZ to string and remove any trailing .0
    data["PLZ"] = data["PLZ"].astype(str)
    data["PLZ"] = data["PLZ"].str.replace(".0", "", regex=False)

    # Get min and max date from the data
    start_date = data["Zeitstempel"].min().strftime("%Y-%m-%d")
    end_date = data["Zeitstempel"].max().strftime("%Y-%m-%d")

    # Get OilPrice for each Tank-ID from OilPriceAPI
    oil_price_api = OilPriceAPI()

    # Get unique PLZ codes
    plz = data["PLZ"].unique()

    all_oil_prices = pd.DataFrame()  # Initialize an empty DataFrame for all oil prices
    # Loop through all unique PLZ codes
    for plz_code in plz:
        print(plz_code)

        # Fetch oil prices for the given PLZ, start date, and end date
        oil_price_df = oil_price_api.get_heizoel(plz_code, start_date, end_date)

        # Add a column for the PLZ code (optional, if you want to keep track of which PLZ each row belongs to)
        oil_price_df["PLZ_Code"] = plz_code

        # Concatenate the fetched DataFrame to the main DataFrame
        all_oil_prices = pd.concat([all_oil_prices, oil_price_df], ignore_index=True)

    # Optionally, reset the index of the final DataFrame
    all_oil_prices.reset_index(drop=True, inplace=True)

    # Rename Date to Zeitstempel
    all_oil_prices.rename(columns={"Date": "Zeitstempel"}, inplace=True)

    # Rename Linear Prozentwert to Prozentualer Füllstand
    data.rename(columns={"Linear Prozentwert": "Prozentualer Füllstand"}, inplace=True)
    # Format to timestamp
    all_oil_prices["Zeitstempel"] = pd.to_datetime(all_oil_prices["Zeitstempel"])

    # Ensure "Zeitstempel" is of the same type in both DataFrames
    data["Zeitstempel"] = pd.to_datetime(data["Zeitstempel"])
    all_oil_prices["Zeitstempel"] = pd.to_datetime(all_oil_prices["Zeitstempel"])

    # Merge the data with the Prices
    data = pd.merge(data, all_oil_prices, on=["Zeitstempel", "PLZ"], how="left")
    data["Oil Price"] = data["Price"]

    # Today DataSet
    today_data = data.sort_values("Zeitstempel").groupby("Tank-ID").tail(1)
    today_data = today_data[
        [
            "Tank-ID",
            "Füllstand",
            "Prozentualer Füllstand",
            "Maximale Füllgrenze",
            "PLZ",
            "Oil Price",
            "Längengrad",
            "Breitengrad",
        ]
    ]

    # Yesterday DataSet
    yesterday_data = data.sort_values("Zeitstempel").groupby("Tank-ID").nth(-2)
    yesterday_data = yesterday_data[
        [
            "Tank-ID",
            "Füllstand",
            "Prozentualer Füllstand",
            "Maximale Füllgrenze",
            "PLZ",
            "Oil Price",
            "Längengrad",
            "Breitengrad",
        ]
    ]

    # Get all Tank-IDs with Latitude and Longitude
    tank_ids_wth = data[["Tank-ID", "Längengrad", "Breitengrad"]].drop_duplicates()

    # for each get the Weather data
    weather_api = WeatherAPI()
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

    results = []
    for index, tank in tank_ids_wth.iterrows():
        tank_id = tank["Tank-ID"]  # Retrieve tank ID
        lat = tank["Breitengrad"]  # Retrieve latitude
        lon = tank["Längengrad"]  # Retrieve longitude

        # Get weather data for the current tank
        weather_data = weather_api.get_data(lat, lon, start_date, end_date)

        # Calculate mean temperature
        mean_temp = weather_data["temperature_2m_mean"].mean()

        results.append((tank_id, mean_temp))

    # Add Results to today_data based on tank_id
    for tank_id, mean_temp in results:
        today_data.loc[today_data["Tank-ID"] == tank_id, "Avg. Temperatur (+15 Tage)"] = mean_temp
        yesterday_data.loc[yesterday_data["Tank-ID"] == tank_id, "Avg. Temperatur (+15 Tage)"] = mean_temp

    # Today DataSet Final
    today_data = today_data[
        [
            "Tank-ID",
            "Füllstand",
            "Prozentualer Füllstand",
            "Maximale Füllgrenze",
            "PLZ",
            "Oil Price",
            "Avg. Temperatur (+15 Tage)",
            "Längengrad",
            "Breitengrad",
        ]
    ]
    today_data["Avg. Temperatur (+15 Tage)"] = today_data["Avg. Temperatur (+15 Tage)"].round(2)

    # Yesterday DataSet Final
    yesterday_data = yesterday_data[
        [
            "Tank-ID",
            "Füllstand",
            "Prozentualer Füllstand",
            "Maximale Füllgrenze",
            "PLZ",
            "Oil Price",
            "Avg. Temperatur (+15 Tage)",
            "Längengrad",
            "Breitengrad",
        ]
    ]
    yesterday_data["Avg. Temperatur (+15 Tage)"] = yesterday_data["Avg. Temperatur (+15 Tage)"].round(2)

    return today_data, yesterday_data


today_data, yesterday_data = load_data("data/processed/data_one_day_clean.pickle")


def view_dashboard_page(CFG: dict) -> None:
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

    # Side Bar Filter
    with st.sidebar:
        # Tank-ID filter (place it at the beginning so it affects the whole page)
        # Today DataSet
        tank_ids = today_data["Tank-ID"].unique()
        selected_tank_ids = st.multiselect(
            "Select Tank-ID(s)", tank_ids, default=tank_ids, key="tank_id1", help="Select one or more Tank-IDs"
        )
        filtered_data_today = today_data[today_data["Tank-ID"].isin(selected_tank_ids)]

        # Yesterday DataSet
        tank_ids = yesterday_data["Tank-ID"].unique()
        filtered_data_yesterday = yesterday_data[yesterday_data["Tank-ID"].isin(selected_tank_ids)]

        # Today - Linearer Prozentwert filter
        max_percentage = st.slider(
            "Select maximum Linearer Prozentwert",
            min_value=0,
            max_value=100,
            value=100,
            step=1,
            help="Filter tanks with Linearer Prozentwert less than or equal to this value",
        )
        filtered_data_today = filtered_data_today[filtered_data_today["Prozentualer Füllstand"] <= max_percentage]

        # Yesterday - Linearer Prozentwert filter
        filtered_data_yesterday = filtered_data_yesterday[
            filtered_data_yesterday["Prozentualer Füllstand"] <= max_percentage
        ]

    # Grid layout for dashboard metrics
    my_grid = grid([2, 2, 2, 2], 1, vertical_align="bottom")

    # Row 1:
    with my_grid.container():
        st.metric(
            "Total Sensors",
            len(filtered_data_today["Tank-ID"].unique()),
            len(filtered_data_today["Tank-ID"].unique()) - len(filtered_data_yesterday["Tank-ID"].unique()),
        )

    with my_grid.container():
        st.metric(
            "Total Liter",
            f"{filtered_data_today['Füllstand'].sum():.0f} liters",
            f"{filtered_data_today['Füllstand'].sum() - filtered_data_yesterday['Füllstand'].sum():.0f}",
        )

    with my_grid.container():
        st.metric(
            "Avg. Utilization in percent",
            f"{filtered_data_today['Prozentualer Füllstand'].mean():.2f}%",
            f"{filtered_data_today['Prozentualer Füllstand'].mean() - filtered_data_yesterday['Prozentualer Füllstand'].mean():.2f}",
        )

    with my_grid.container():
        avg_oil_price_today = filtered_data_today["Oil Price"].mean()
        avg_oil_price_yesterday = filtered_data_yesterday["Oil Price"].mean()
        st.metric(
            "Avg. Heating Oil Price:",
            f"{avg_oil_price_today:.2f} EUR",
            f"{avg_oil_price_today - avg_oil_price_yesterday:.2f} EUR",
            delta_color="inverse",
        )

    # Row 2: Display Tank information
    with my_grid.container():
        # Create tabs for Today and Yesterday data
        tab1, tab2, tab3 = st.tabs(["Today", "Yesterday", "GeoMap"])

        with tab1:
            st.dataframe(
                filtered_data_today.sort_values("Tank-ID"),
                column_config={
                    "Prozentualer Füllstand": st.column_config.ProgressColumn(
                        "Prozentualer Füllstand",
                        help="The linear percentage value",
                        format="%f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
                use_container_width=True,  # Set this to True for full-width display
            )

        with tab2:
            st.dataframe(
                filtered_data_yesterday.sort_values("Tank-ID"),
                column_config={
                    "Prozentualer Füllstand": st.column_config.ProgressColumn(
                        "Prozentualer Füllstand",
                        help="The linear percentage value",
                        format="%f%%",
                        min_value=0,
                        max_value=100,
                    ),
                },
                hide_index=True,
                use_container_width=True,  # Set this to True for full-width display
            )

        with tab3:
            # Karte erstellen mit Plotly
            fig = px.scatter_mapbox(
                today_data,
                lat="Breitengrad",
                lon="Längengrad",
                size="Prozentualer Füllstand",  # Größe der Punkte nach Prozentualer Füllstand
                hover_name="Tank-ID",
                hover_data=["Füllstand", "Oil Price"],
                color_discrete_sequence=["blue"],
                zoom=10,
                height=600,
            )

            # Plotly Mapbox Stil setzen
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

            # In Streamlit anzeigen
            st.plotly_chart(fig)


# Call the dashboard function
view_dashboard_page(CFG={})
