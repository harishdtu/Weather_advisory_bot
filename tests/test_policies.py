from app.policies.loader import load_sops
from app.policies.evaluator import sop_matches
from app.llm.intent import parse_intent_simple


def test_load_sops():
    sops = load_sops("policies/sops.yaml")
    assert len(sops) >= 10


def test_sop_match_simple():
    sops = load_sops("policies/sops.yaml")
    # build a weather dict that should match strong wind cycling
    weather = {"current": {"wind_speed_10m": 45}}
    intent = {"activity": "cycling"}
    matched = [s for s in sops if sop_matches(s, weather, intent)]
    assert any(s.id == "SOP-01" for s in matched)


def test_activity_aliases_are_recognized():
    for raw_activity, expected in {
        "running": "run",
        "run": "run",
        "jogging": "run",
        "jog": "run",
        "runner": "run",
        "cycling": "cycle",
        "cycle": "cycle",
        "biking": "cycle",
        "bike": "cycle",
        "hiking": "walk",
        "hike": "walk",
        "walking": "walk",
        "walk": "walk",
    }.items():
        intent = parse_intent_simple(f"Can I go {raw_activity} today in Bangalore?")
        assert intent["activity"] == expected
