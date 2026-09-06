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
