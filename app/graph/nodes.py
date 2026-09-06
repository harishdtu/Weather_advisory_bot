from typing import Dict, Any
from app.llm.intent import parse_intent_simple
from app.weather.client import WeatherClient, WeatherError
from app.policies.loader import load_sops
from app.policies.evaluator import sop_matches, rank_sops
import logging

logger = logging.getLogger(__name__)


SOPS_PATH = "policies/sops.yaml"


def node_parse_user_request(state: Dict[str, Any]):
    text = state.get("raw_input")
    prior_intent = state.get("intent") or {}
    intent = parse_intent_simple(text)
    merged = dict(prior_intent)
    for key, value in intent.items():
        if value is not None:
            merged[key] = value
    if not merged.get("location") and prior_intent.get("location"):
        merged["location"] = prior_intent.get("location")
    state["intent"] = merged
    return state


def node_resolve_location(state: Dict[str, Any]):
    intent = state.get("intent", {})
    loc_text = intent.get("location")
    if not loc_text:
        # try to find any capitalized token in the raw input
        words = state.get("raw_input", "").split()
        for w in words[::-1]:
            if w.istitle():
                loc_text = w
                break

    if not loc_text:
        state["error"] = {"type": "no_location", "message": "No location found in request"}
        return state

    wc = WeatherClient()
    try:
        loc = wc.resolve_city(loc_text)
    except WeatherError as e:
        state["error"] = {"type": str(e), "message": "Could not resolve location"}
        return state

    # use Pydantic model_dump to avoid deprecation
    state["location"] = loc.model_dump()
    return state


def node_fetch_weather(state: Dict[str, Any]):
    loc = state.get("location")
    if not loc:
        state["error"] = {"type": "no_location", "message": "No resolved location"}
        return state

    wc = WeatherClient()
    try:
        wr = wc.fetch_weather(latitude=loc["latitude"], longitude=loc["longitude"]) 
    except WeatherError as e:
        state["error"] = {"type": str(e), "message": "Could not fetch weather"}
        return state

    # return raw values as dict
    state["weather"] = wr.raw
    # also attach normalized current
    state["weather"]["current"] = {
        "temperature_2m": wr.current.temperature_2m,
        "wind_speed_10m": wr.current.wind_speed_10m,
        "wind_gusts_10m": wr.current.wind_gusts_10m,
        "precipitation": wr.current.precipitation,
        "precipitation_probability": wr.current.precipitation_probability,
        "uv_index": wr.current.uv_index,
        "weather_code": wr.current.weather_code,
    }

    return state


def node_match_sops(state: Dict[str, Any]):
    sops = load_sops(SOPS_PATH)
    matched = []
    weather = state.get("weather", {})
    intent = state.get("intent", {})
    for s in sops:
        if sop_matches(s, weather, intent):
            matched.append(s)

    state["matched_sops"] = [s.id for s in matched]
    if not matched:
        state["no_policy"] = True
        return state

    ranked = rank_sops(matched)
    state["selected_sop"] = ranked[0].model_dump()
    state["matched_sops_full"] = [s.model_dump() for s in matched]
    return state


def node_compose_response(state: Dict[str, Any]):
    # Build the decision structure for composer
    if state.get("no_policy"):
        state["decision"] = {
            "status": "no_policy",
            "message": "I don't have a policy that covers this situation, so no SOP applies. I can't provide a safety recommendation.",
            "weather": state.get("weather"),
        }
        return state

    if state.get("error"):
        state["decision"] = {"status": "weather_unavailable", "message": "I couldn't retrieve the required live weather data for that location, so I can't provide a weather-based recommendation right now."}
        return state

    policy = state.get("selected_sop")
    weather = state.get("weather")

    # reason: simple explanation
    reason = "Matches policy conditions based on current weather and activity."

    recommendation = policy.get("guidance") or "Follow policy guidance."

    state["decision"] = {
        "status": "success",
        "recommendation": recommendation,
        "policy": policy,
        "weather": weather,
        "reason": reason,
        "location": state.get("location"),
    }

    return state
