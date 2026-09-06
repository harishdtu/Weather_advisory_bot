from app.graph.workflow import LangGraphRunner
from app.weather.client import WeatherClient, WeatherError


def make_weather_response(current):
    class C:
        def __init__(self, payload):
            self.temperature_2m = payload.get("temperature_2m")
            self.wind_speed_10m = payload.get("wind_speed_10m")
            self.wind_gusts_10m = payload.get("wind_gusts_10m")
            self.precipitation = payload.get("precipitation")
            self.precipitation_probability = payload.get("precipitation_probability")
            self.uv_index = payload.get("uv_index")
            self.weather_code = payload.get("weather_code")

    class R:
        def __init__(self, payload):
            self.raw = payload
            self.current = C(payload.get("current", {}))

    return R({"timezone": "UTC", "current": current})


original_resolve = WeatherClient.resolve_city
original_fetch = WeatherClient.fetch_weather

# A. Normal question + session follow-up
WeatherClient.resolve_city = lambda self, city: type("L", (), {"model_dump": lambda self=None, city=city: {"name": city, "latitude": 17.385, "longitude": 78.4867}})()
WeatherClient.fetch_weather = lambda self, latitude, longitude, timezone="UTC": make_weather_response({
    "temperature_2m": 28,
    "wind_speed_10m": 45,
    "wind_gusts_10m": 55,
    "precipitation": 0,
    "precipitation_probability": 20,
    "uv_index": 5,
    "weather_code": 0,
})
runner = LangGraphRunner()
print("A", runner.run("session-a", "is it safe to cycle today in Hyderabad?"))
print("B", runner.run("session-a", "what about this evening?"))

# C. No-policy question
WeatherClient.fetch_weather = lambda self, latitude, longitude, timezone="UTC": make_weather_response({
    "temperature_2m": 21,
    "wind_speed_10m": 4,
    "wind_gusts_10m": 6,
    "precipitation": 0,
    "precipitation_probability": 0,
    "uv_index": 2,
    "weather_code": 0,
})
print("C", runner.run("session-c", "is it safe to go stargazing in Pune?"))

# D. Location failure
WeatherClient.resolve_city = lambda self, city: (_ for _ in ()).throw(WeatherError("geocoding_no_results"))
print("D", runner.run("session-d", "is it safe to cycle in Atlantis?"))

# E. Weather failure
WeatherClient.resolve_city = lambda self, city: type("L", (), {"model_dump": lambda self=None, city=city: {"name": city, "latitude": 17.385, "longitude": 78.4867}})()
WeatherClient.fetch_weather = lambda self, latitude, longitude, timezone="UTC": (_ for _ in ()).throw(WeatherError("forecast_unavailable"))
print("E", runner.run("session-e", "is it safe to cycle in Hyderabad?"))

# restore original methods
WeatherClient.resolve_city = original_resolve
WeatherClient.fetch_weather = original_fetch
