import pytest
from app.graph.workflow import LangGraphRunner
from app.weather.client import WeatherError, WeatherClient


def test_no_policy_branch(monkeypatch):
    # Setup resolve_city and fetch_weather to return a location and weather that matches no SOP
    # model_dump must accept an optional self argument when called as a method
    monkeypatch.setattr(WeatherClient, "resolve_city", lambda self, city: type("L", (), {"model_dump": (lambda self=None, city=city: {"name": city, "latitude": 0.0, "longitude": 0.0})})())

    def fake_fetch(self, latitude, longitude, timezone="UTC"):
        class WR:
            raw = {"timezone": "UTC"}
            current = type("C", (), {"temperature_2m": 20, "wind_speed_10m": 1, "wind_gusts_10m": 0, "precipitation": 0, "precipitation_probability": 0, "uv_index": 1, "weather_code": 0})
        return WR()

    monkeypatch.setattr(WeatherClient, "fetch_weather", fake_fetch)

    runner = LangGraphRunner()
    state = runner.run("sess-no-policy", "Is it safe to go stargazing in Nowhereville?")
    decision = state.get("decision")
    assert decision is not None
    assert decision.get("status") == "no_policy"


def test_geocoding_failure(monkeypatch):
    monkeypatch.setattr(WeatherClient, "resolve_city", lambda self, city: (_ for _ in ()).throw(WeatherError("geocoding_unavailable")))
    runner = LangGraphRunner()
    state = runner.run("sess-fail", "Is it safe to cycle in Atlantis?")
    decision = state.get("decision")
    assert decision is not None
    assert decision.get("status") == "weather_unavailable"
