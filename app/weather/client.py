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

        query_norm = (city or "").strip().lower()
        city_aliases = {
            "bangalore": ["bangalore", "bengaluru"],
            "bengaluru": ["bengaluru", "bangalore"],
        }
        preferred = None
        candidate_names = city_aliases.get(query_norm, [query_norm])
        for alias in candidate_names:
            for res in results:
                name = (res.get("name") or "").strip()
                name_norm = name.lower()
                if name_norm == alias:
                    preferred = res
                    break
            if preferred is not None:
                break

        if preferred is None:
            for alias in candidate_names:
                for res in results:
                    name = (res.get("name") or "").strip()
                    name_norm = name.lower()
                    normalized_name = name_norm.replace(" town", "").replace(" city", "").strip()
                    if normalized_name == alias:
                        preferred = res
                        break
                if preferred is not None:
                    break

        if preferred is None:
            best_score = -1
            for res in results:
                name = (res.get("name") or "").strip()
                name_norm = name.lower()
                score = 0
                if name_norm == query_norm:
                    score += 100
                elif query_norm in name_norm:
                    score += 20
                if "town" in name_norm:
                    score -= 10
                if "district" in name_norm:
                    score -= 10
                if score > best_score:
                    best_score = score
                    preferred = res

        if preferred is None:
            preferred = results[0]

        try:
            loc = Location(
                name=preferred.get("name"),
                country=preferred.get("country"),
                latitude=float(preferred.get("latitude")),
                longitude=float(preferred.get("longitude")),
                admin1=preferred.get("admin1"),
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

        hourly = data.get("hourly") or {}
        current_weather = data.get("current_weather") or {}
        current_time = current_weather.get("time")
        current_index = None
        if current_time:
            times = hourly.get("time") or []
            for i, t in enumerate(times):
                if t.startswith(current_time[:13]):
                    current_index = i
                    break
            if current_index is None and times:
                current_index = 0

        def pick_value(field: str, fallback: Optional[float] = None):
            if current_weather.get(field) is not None:
                return current_weather.get(field)
            if current_index is not None:
                values = hourly.get(field)
                if values and len(values) > current_index:
                    value = values[current_index]
                    if value is not None:
                        return value
            if fallback is not None:
                return fallback
            return None

        # open-meteo exposes current conditions under current_weather and hourly values for
        # UV/probability/gusts; use the hourly value at the same timestamp when current data is absent.
        try:
            current = WeatherCurrent(
                temperature_2m=pick_value("temperature"),
                wind_speed_10m=pick_value("windspeed"),
                wind_gusts_10m=pick_value("wind_gusts_10m"),
                precipitation=pick_value("precipitation"),
                precipitation_probability=pick_value("precipitation_probability"),
                uv_index=pick_value("uv_index"),
                apparent_temperature=pick_value("apparent_temperature"),
                weather_code=pick_value("weathercode"),
                raw=current_weather,
            )
        except ValidationError as e:
            logger.exception("Invalid current weather schema")
            raise WeatherError("forecast_invalid") from e

        return WeatherResponse(timezone=data.get("timezone"), current=current, raw=data)
