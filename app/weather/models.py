from typing import Optional, Dict, Any
from pydantic import BaseModel


class Location(BaseModel):
    name: str
    country: Optional[str]
    latitude: float
    longitude: float
    admin1: Optional[str]


class WeatherCurrent(BaseModel):
    temperature_2m: Optional[float]
    wind_speed_10m: Optional[float]
    wind_gusts_10m: Optional[float]
    precipitation: Optional[float]
    precipitation_probability: Optional[float]
    uv_index: Optional[float]
    apparent_temperature: Optional[float]
    weather_code: Optional[int]
    raw: Dict[str, Any] = {}


class WeatherResponse(BaseModel):
    timezone: Optional[str]
    current: WeatherCurrent
    raw: Dict[str, Any] = {}
