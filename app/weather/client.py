import httpx
from typing import Optional, Dict, Any
from .models import Location, WeatherResponse, WeatherCurrent
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class WeatherError(Exception):
    pass


class WeatherClient:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def resolve_city(self, city: str) -> Location:
        params = {"name": city, "count": 5}
        try:
            resp = httpx.get(GEOCODE_URL, params=params, timeout=self.timeout)
        except Exception as e:
            logger.exception("Geocoding request failed")
            raise WeatherError("geocoding_unavailable") from e

        if resp.status_code != 200:
            raise WeatherError("geocoding_failed")

        try:
            data = resp.json()
        except Exception as e:
            logger.exception("Malformed geocoding JSON")
            raise WeatherError("geocoding_malformed") from e

        results = data.get("results") or []
        if not results:
            raise WeatherError("geocoding_no_results")

        first = results[0]
        try:
            loc = Location(
                name=first.get("name"),
                country=first.get("country"),
                latitude=float(first.get("latitude")),
                longitude=float(first.get("longitude")),
                admin1=first.get("admin1"),
            )
        except Exception as e:
            logger.exception("Invalid geocoding data")
            raise WeatherError("geocoding_invalid") from e

        return loc

    def fetch_weather(self, latitude: float, longitude: float, timezone: str = "UTC") -> WeatherResponse:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ",".join([
                "temperature_2m",
                "wind_speed_10m",
                "wind_gusts_10m",
                "precipitation",
                "weather_code",
                "uv_index",
                "apparent_temperature",
            ]),
            "hourly": ",".join([
                "temperature_2m",
                "precipitation_probability",
                "precipitation",
                "wind_speed_10m",
                "wind_gusts_10m",
                "uv_index",
                "weather_code",
            ]),
            "daily": ",".join([
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
            ]),
            "current_weather": True,
            "forecast_days": 1,
            "timezone": timezone,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        }

        try:
            resp = httpx.get(FORECAST_URL, params=params, timeout=self.timeout)
        except Exception as e:
            logger.exception("Forecast request failed")
            raise WeatherError("forecast_unavailable") from e

        if resp.status_code != 200:
            raise WeatherError("forecast_failed")

        try:
            data = resp.json()
        except Exception as e:
            logger.exception("Malformed forecast JSON")
            raise WeatherError("forecast_malformed") from e

        # Extract current weather info
        cw = data.get("current_weather") or {}
        # open-meteo sometimes returns different fields; map carefully
        try:
            current = WeatherCurrent(
                temperature_2m=cw.get("temperature"),
                wind_speed_10m=cw.get("windspeed"),
                wind_gusts_10m=None,
                precipitation=None,
                precipitation_probability=None,
                uv_index=None,
                apparent_temperature=None,
                weather_code=cw.get("weathercode"),
                raw=cw,
            )
        except ValidationError as e:
            logger.exception("Invalid current weather schema")
            raise WeatherError("forecast_invalid") from e

        return WeatherResponse(timezone=data.get("timezone"), current=current, raw=data)
