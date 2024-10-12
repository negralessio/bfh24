from datetime import datetime
import requests
import pandas as pd


class OilPriceAPI:
    """
    A class to interact with the Heizöl24 API to retrieve heating oil price data.

    Attributes:
    ----------
    heizoel24url : str
        The base URL for the Heizöl24 API endpoint to fetch historical local prices.

    Methods:
    -------
    get_heizoel(plz, start_date, end_date=None):
        Retrieves heating oil price data for a specified postal code and date range.
    """

    def __init__(self):
        """
        Initializes the OilPriceAPI instance, setting up the API URL.
        """
        self.heizoel24url = "https://www.heizoel24.de/api/site/1/{}/prices/history-local?"

    def get_heizoel(self, plz, start_date, end_date=None):
        """
        Retrieves heating oil price data from the Heizöl24 API for a given postal code
        and date range.

        Parameters:
        ----------
        plz : str
            The postal code for which to retrieve heating oil prices.

        start_date : str
            The start date for the data retrieval in the format 'YYYY-MM-DD'.

        end_date : str, optional
            The end date for the data retrieval in the format 'YYYY-MM-DD'.
            If not provided, the current date is used as the default end date.

        Returns:
        -------
        pandas.DataFrame
            A DataFrame containing the heating oil prices within the specified date range,
            with the following columns:
                - Date : str
                    The date of the price.
                - Price : float
                    The price of heating oil on that date.
                - PLZ : str
                    The postal code provided in the request.
            If the request fails or if no data is found, None is returned.
        """
        current_date = datetime.now().strftime("%Y-%m-%d")

        if end_date is None or end_date > current_date:
            end_date = current_date  # Use the current date as the default end date

        heizoel24url_api = self.heizoel24url.format(plz)

        params = {"rangeType": 7, "withEndDate": False, "productGroup": "heizöl"}

        response = requests.get(heizoel24url_api, params=params)

        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None

        df = pd.DataFrame(data)

        df["DateTime"] = pd.to_datetime(df["DateTime"])

        df["Date"] = df["DateTime"].dt.strftime("%Y-%m-%d")

        df.drop(columns="DateTime", inplace=True)

        df["Measurement"] = "EUR/100L"  # Add a new column for the currency

        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

        df["PLZ"] = plz

        return df
