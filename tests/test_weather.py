import pytest
from app.weather.client import WeatherClient, WeatherError


def test_geocode_no_results(monkeypatch):
    class Dummy:
        status_code = 200
        def json(self):
            return {"results": []}

    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: Dummy())
    wc = WeatherClient()
    with pytest.raises(WeatherError):
        wc.resolve_city("SomeUnknownPlace")


def test_resolve_city_prefers_exact_name_match(monkeypatch):
    class Dummy:
        status_code = 200
        def json(self):
            return {
                "results": [
                    {"name": "Bangalore Town", "country": "Pakistan", "latitude": 24.87, "longitude": 67.08},
                    {"name": "Bangalore", "country": "India", "latitude": 12.97, "longitude": 77.59},
                ]
            }

    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: Dummy())
    wc = WeatherClient()
    loc = wc.resolve_city("Bangalore")
    assert loc.name == "Bangalore"
    assert loc.country == "India"
