import pandas as pd


def get_recommendation(context_num, forcast_num, tank_id):
    """Get the recommendation for the oil consumption and price forecasting."""
    oil_consumption_df = run_oil_consumption_forecasting(context_num, forcast_num, tank_id)
    oil_price_df = run_oil_price_forecasting(context_num, forcast_num, tank_id)

    # Get today values
    today = oil_consumption_df.index
    today_oil_tank_level = oil_consumption_df.loc[today, "Füllstand"]  # In Liters

    return recommendation
