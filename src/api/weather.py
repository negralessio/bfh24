import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime


class WeatherAPI:
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

        def get_history_data(params):
            # Get the historical weather data
            response = self.openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
            # Process daily data. The order of variables needs to be the same as requested.
            print(dir(response[0].Daily()))

            return response

        def get_forecast_data(params):
            # Get the forecast weather data
            response = self.openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
            daily = response.get("daily", [])
            forecast_data = pd.DataFrame(daily)
            return forecast_data

        # Determine if we need to call both APIs or just the history API
        if end_date > current_date:
            # Call both APIs

            # Calculate the number of days between the end_date and current_date
            days_difference = (
                datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(current_date, "%Y-%m-%d")
            ).days

            # Ensure the forecast days do not exceed the maximum lookahead of 16 days
            forecast_days = min(days_difference, 16)

            # Historical weather data parameters
            params_history = {
                "latitude": latitude,
                "longitude": longitude,
                "start": start_date,
                "end": current_date,
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
                "forecast_days": forecast_days,
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
                "start": start_date,
                "end": current_date,
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


def main():
    # Example usage
    weather_api = WeatherAPI()
    data = weather_api.get_data(latitude=47.3769, longitude=8.5417, start_date="2023-01-01", end_date="2023-01-10")
    print(data)


if __name__ == "__main__":
    main()
