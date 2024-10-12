import pandas as pd
import streamlit as st
from streamlit_extras.grid import grid
import plotly.graph_objects as go


def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_pickle(file_path)
    print(data.head())

    # Remove all with Tank-ID = 5
    data = data[data["Tank-ID"] != 5]

    # Add Oil Prices

    # Today DataSet
    today_data = data.sort_values("Zeitstempel").groupby("Tank-ID").tail(1)
    today_data = today_data[["Tank-ID", "Füllstand", "Linear Prozentwert", "Maximale Füllgrenze", "Temperatur", "PLZ"]]

    # Yesterday DataSet
    yesterday_data = data.sort_values("Zeitstempel").groupby("Tank-ID").nth(-2)
    yesterday_data = yesterday_data[
        ["Tank-ID", "Füllstand", "Linear Prozentwert", "Maximale Füllgrenze", "Temperatur", "PLZ"]
    ]

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
        filtered_data_today = filtered_data_today[filtered_data_today["Linear Prozentwert"] <= max_percentage]

        # Yesterday - Linearer Prozentwert filter
        filtered_data_yesterday = filtered_data_yesterday[
            filtered_data_yesterday["Linear Prozentwert"] <= max_percentage
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
            f"{filtered_data_today['Linear Prozentwert'].mean():.2f}%",
            f"{filtered_data_today['Linear Prozentwert'].mean() - filtered_data_yesterday['Linear Prozentwert'].mean():.2f}",
        )

    with my_grid.container():
        st.metric("Avg. Heating Oil Price:", "0.00 Euro", "1", delta_color="inverse")

    # Row 2: Display Tank information
    with my_grid.container():
        # Create tabs for Today and Yesterday data
        tab1, tab2, tab3 = st.tabs(["Today", "Yesterday", "GeoMap"])

        with tab1:
            st.dataframe(
                filtered_data_today.sort_values("Tank-ID"),
                column_config={
                    "Linear Prozentwert": st.column_config.ProgressColumn(
                        "Linearer Prozentwert",
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
                    "Linear Prozentwert": st.column_config.ProgressColumn(
                        "Linearer Prozentwert",
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
            st.header("TBD")


# Call the dashboard function
view_dashboard_page(CFG={})
