from app.llm.intent import parse_intent_simple
from app.graph.nodes import node_parse_user_request, node_match_sops
from app.policies.loader import load_sops


def test_parse_activities():
    assert parse_intent_simple("Can I go running today in Bangalore?")["activity"] == "run"
    assert parse_intent_simple("Is it safe to cycle today in Hyderabad?")["activity"] == "cycle"
    assert parse_intent_simple("Can I go jogging today in Bangalore?")["activity"] == "run"
    assert parse_intent_simple("Is today suitable for a picnic?")["activity"] == "picnic"
    assert parse_intent_simple("Should I take my kid to the park?")["group"] == "children"


def make_state(text, weather):
    state = {"raw_input": text}
    state = node_parse_user_request(state)
    state["weather"] = weather
    state = node_match_sops(state)
    return state


def test_running_sop_matches_by_uv():
    # UV high triggers SOP-02 (outdoor_exercise)
    weather = {"current": {"uv_index": 9, "temperature_2m": 30, "wind_speed_10m": 5, "wind_gusts_10m": 0, "precipitation": 0, "precipitation_probability": 0, "weather_code": 0}}
    s = make_state("Can I go running today in Bangalore?", weather)
    assert not s.get("no_policy")
    assert any("outdoor_exercise" in sop.get("category", "") or sop.get("category") == "outdoor_exercise" for sop in s.get("matched_sops_full", []))


def test_cycling_sop_matches_by_wind():
    weather = {"current": {"wind_speed_10m": 45, "uv_index": 3, "temperature_2m": 25, "wind_gusts_10m": 0, "precipitation": 0, "precipitation_probability": 0, "weather_code": 0}}
    s = make_state("Is it safe to cycle today in Hyderabad?", weather)
    assert not s.get("no_policy")
    assert any(sop.get("category") == "cycling" for sop in s.get("matched_sops_full", []))


def test_picnic_sop():
    weather = {"current": {"precipitation_probability": 10, "temperature_2m": 20, "uv_index": 5, "wind_speed_10m": 5, "wind_gusts_10m": 0, "precipitation": 0, "weather_code": 0}}
    s = make_state("Is today suitable for a picnic?", weather)
    assert not s.get("no_policy")
    assert any(sop.get("category") == "picnic" for sop in s.get("matched_sops_full", []))


def test_children_park_sop():
    weather = {"current": {"wind_gusts_10m": 60, "temperature_2m": 20, "uv_index": 3, "wind_speed_10m": 5, "precipitation": 0, "precipitation_probability": 0, "weather_code": 0}}
    s = make_state("Should I take my kid to the park?", weather)
    assert not s.get("no_policy")
    assert any(sop.get("category") == "children" for sop in s.get("matched_sops_full", []))


def test_genuine_no_sop():
    # random unsupported activity
    weather = {"current": {"temperature_2m": 20, "uv_index": 1, "wind_speed_10m": 1, "wind_gusts_10m": 0, "precipitation": 0, "precipitation_probability": 0, "weather_code": 0}}
    s = make_state("Can I use a chainsaw today?", weather)
    assert s.get("no_policy")
