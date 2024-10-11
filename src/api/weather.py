import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry


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

    def get_weather_data(self, latitude, longitude, start_date, end_date):
        # Historical weather data Parameter
        params_history = {
            "latitude": latitude,
            "longitude": longitude,
            "start": start_date,
            "end": end_date,
            "hourly": True,
        }

        # Get forecast weather data Parameter
        params_forecast = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": 5,
        }

        return None
