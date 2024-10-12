import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime


class WeatherAPI:
    """
    A class to interact with the Open-Meteo API to retrieve historical and forecast weather data.
    This class uses caching and retry mechanisms for reliable API requests.

    Attributes:
        api_key (str): The API key for authenticating with the Open-Meteo API (currently set to None, extendable for future use).
        history_url (str): The URL endpoint for accessing historical weather data from the Open-Meteo API.
        forecast_url (str): The URL endpoint for accessing forecast weather data from the Open-Meteo API.
        openmeteo (Client): A client object that makes HTTP requests to the Open-Meteo API, with caching enabled and automatic retries.

    Methods:
        get_data(latitude, longitude, start_date, end_date):
            Fetches both historical and forecast weather data based on the specified location and date range.
            If the `end_date` exceeds the current date, both historical and forecast data are retrieved; otherwise, only historical data is fetched.

        get_history_data(params):
            Helper method that retrieves historical weather data from the Open-Meteo API using the provided parameters.
            Returns the data as a pandas DataFrame.

        get_forecast_data(params):
            Helper method that retrieves forecast weather data from the Open-Meteo API using the provided parameters.
            Returns the data as a pandas DataFrame.

    Usage:
        - Instantiate the class and call the `get_data` method to retrieve weather data for a specified latitude, longitude, and date range.
        - The returned data is processed into a pandas DataFrame, containing daily weather metrics such as temperature, apparent temperature, sunshine duration, and precipitation.
        - Historical data can be fetched for a wide range of dates, while forecast data can only be fetched up to 16 days in the future.

    Example:
        weather_api = WeatherAPI()
        data = weather_api.get_data(latitude=48.8566, longitude=2.3522, start_date="2023-09-01", end_date="2023-09-15")
        print(data)

    """

    def __init__(self):
        # Hier API-Key eintragen etc. eintragen oder erweitern
        self.api_key = None
        self.history_url = "https://archive-api.open-meteo.com/v1/archive"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"

        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession(".cache", expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_data(self, latitude, longitude, start_date, end_date):
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Calculate the date one day before the current date
        param_day = (datetime.now() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")

        def get_history_data(params):
            # Get the historical weather data
            responses = self.openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
            # Process daily data. The order of variables needs to be the same as requested.
            response = responses[0]

            # Daten aus der täglichen Antwort extrahieren
            daily = response.Daily()

            # Variablen extrahieren und in ein Wörterbuch packen
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left",
                ),
                "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
                "temperature_2m_mean": daily.Variables(2).ValuesAsNumpy(),
                "apparent_temperature_max": daily.Variables(3).ValuesAsNumpy(),
                "apparent_temperature_min": daily.Variables(4).ValuesAsNumpy(),
                "apparent_temperature_mean": daily.Variables(5).ValuesAsNumpy(),
                "sunshine_duration": daily.Variables(6).ValuesAsNumpy(),
                "precipitation_sum": daily.Variables(7).ValuesAsNumpy(),
                "rain_sum": daily.Variables(8).ValuesAsNumpy(),
                "snowfall_sum": daily.Variables(9).ValuesAsNumpy(),
            }

            # In ein DataFrame umwandeln und anzeigen
            daily_history = pd.DataFrame(daily_data)
            # print(daily_history)

            return daily_history

        def get_forecast_data(params):
            # Get the forecast weather data
            responses = self.openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)

            # Process daily data. The order of variables needs to be the same as requested.
            response = responses[0]

            # Daten aus der täglichen Antwort extrahieren
            daily = response.Daily()

            # Variablen extrahieren und in ein Wörterbuch packen
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left",
                ),
                "temperature_2m_max": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(1).ValuesAsNumpy(),
                "temperature_2m_mean": daily.Variables(2).ValuesAsNumpy(),
                "apparent_temperature_max": daily.Variables(3).ValuesAsNumpy(),
                "apparent_temperature_min": daily.Variables(4).ValuesAsNumpy(),
                "apparent_temperature_mean": daily.Variables(5).ValuesAsNumpy(),
                "sunshine_duration": daily.Variables(6).ValuesAsNumpy(),
                "precipitation_sum": daily.Variables(7).ValuesAsNumpy(),
                "rain_sum": daily.Variables(8).ValuesAsNumpy(),
                "snowfall_sum": daily.Variables(9).ValuesAsNumpy(),
            }

            # In ein DataFrame umwandeln und anzeigen
            daily_forecast = pd.DataFrame(daily_data)
            # print(daily_forecast)

            return daily_forecast

        # Determine if we need to call both APIs or just the history API
        if end_date > current_date:
            # Call both APIs

            # Calculate the number of days between the end_date and current_date
            days_difference = (
                datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(current_date, "%Y-%m-%d")
            ).days

            # Ensure the forecast days do not exceed the maximum lookahead of 16 days
            forecast_days = min(days_difference, 16)
            print(forecast_days)
            # Historical weather data parameters
            params_history = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": param_day,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "apparent_temperature_mean",
                    "sunshine_duration",
                    "precipitation_sum",
                    "rain_sum",
                    "snowfall_sum",
                ],
            }
            # Forecast weather data parameters
            params_forecast = {
                "latitude": latitude,
                "longitude": longitude,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "apparent_temperature_mean",
                    "sunshine_duration",
                    "precipitation_sum",
                    "rain_sum",
                    "snowfall_sum",
                ],
                "forecast_days": forecast_days + 1,
            }

            history = get_history_data(params_history)
            forecast = get_forecast_data(params_forecast)

            # Combine both DataFrames
            combined_data = pd.concat([history, forecast], ignore_index=True)
            return combined_data

        else:
            # Call only the history API
            params_history = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "apparent_temperature_max",
                    "apparent_temperature_min",
                    "apparent_temperature_mean",
                    "sunshine_duration",
                    "precipitation_sum",
                    "rain_sum",
                    "snowfall_sum",
                ],
            }

            history = get_history_data(params_history)
            return history
