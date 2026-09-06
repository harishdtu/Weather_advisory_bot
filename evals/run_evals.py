import yaml
import sys
sys.path.insert(0, '.')
from app.graph.workflow import LangGraphRunner
from app.weather.client import WeatherClient, WeatherError


def _make_weather_response(payload):
    class _C:
        def __init__(self, d):
            self.temperature_2m = d.get("temperature_2m")
            self.wind_speed_10m = d.get("wind_speed_10m")
            self.wind_gusts_10m = d.get("wind_gusts_10m")
            self.precipitation = d.get("precipitation")
            self.precipitation_probability = d.get("precipitation_probability")
            self.uv_index = d.get("uv_index")
            self.weather_code = d.get("weather_code")

    class _R:
        def __init__(self, d):
            self.raw = d
            self.current = _C(d.get("current", {}))

    return _R(payload)


def run():
    with open("evals/cases.yaml", "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    results = []
    total = 0
    passed = 0
    for c in data.get("cases", []):
        total += 1
        session_id = f"eval-{c['name']}"
        runner = LangGraphRunner()

        mock_weather = c.get("mock_weather")
        if c.get("force_weather_error"):
            original_fetch = WeatherClient.fetch_weather
            WeatherClient.fetch_weather = lambda self, latitude, longitude, timezone="UTC": (_ for _ in ()).throw(WeatherError("forecast_unavailable"))
            try:
                state = runner.run(session_id, c["query"])
            finally:
                WeatherClient.fetch_weather = original_fetch
        elif mock_weather:
            original_fetch = WeatherClient.fetch_weather
            original_resolve = WeatherClient.resolve_city
            WeatherClient.resolve_city = lambda self, city: type("L", (), {"model_dump": lambda self=None, city=city: {"name": city, "latitude": 17.385, "longitude": 78.4867}})()
            WeatherClient.fetch_weather = lambda self, latitude, longitude, timezone="UTC": _make_weather_response(mock_weather)
            try:
                state = runner.run(session_id, c["query"])
            finally:
                WeatherClient.fetch_weather = original_fetch
                WeatherClient.resolve_city = original_resolve
        else:
            state = runner.run(session_id, c["query"])

        decision = state.get("decision") or {}
        status = decision.get("status")
        policy = (decision.get("policy") or {}).get("id") if isinstance(decision.get("policy"), dict) else None
        actual = {
            "case": c["name"],
            "query": c["query"],
            "status": status,
            "policy": policy,
            "decision": decision,
        }

        expected = c.get("expected_status")
        desired_policy = c.get("expected_policy")
        ok = status == expected
        if desired_policy:
            ok = ok and policy == desired_policy
        if c.get("must_contain"):
            msg = str(decision.get("message") or decision.get("recommendation") or "")
            ok = ok and c["must_contain"] in msg

        actual["PASS"] = ok
        results.append(actual)
        passed += 1 if ok else 0

        print(f"CASE: {c['name']}")
        print(f"  query: {c['query']}")
        print(f"  expected_status: {expected} expected_policy: {desired_policy}")
        print(f"  actual_status: {status} actual_policy: {policy}")
        print(f"  PASS" if ok else "  FAIL")

    print(f"Evals complete: {passed}/{total} passed")
    if passed != total:
        raise SystemExit(1)
    return results


if __name__ == "__main__":
    run()
