from typing import List, Dict, Any
from .models import SOP
import operator
import re

OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}

ACTIVITY_ALIASES = {
    "run": {"run", "running", "runner", "jog", "jogging", "exercise", "outdoor exercise", "workout"},
    "cycle": {"cycle", "cycling", "bicycle", "bike", "biking", "ride", "riding", "cyclist"},
    "walk": {"walk", "walking", "hike", "hiking", "hiker", "trek", "trekking", "stroll", "strolling"},
    "picnic": {"picnic", "picnicking", "outdoor meal"},
    "travel": {"travel", "commute", "drive", "driving", "trip"},
    "park": {"park", "play", "playing", "playground"},
    "pets": {"pet", "pets", "dog", "dog walk", "walk dog"},
}


def evaluate_condition(cond, weather: Dict[str, Any], intent: Dict[str, Any]) -> bool:
    # cond.field can be like 'current.wind_speed_10m'
    # resolve field
    parts = cond.field.split(".")
    val = None
    if parts[0] == "current":
        val = weather.get("current", {}).get(parts[1])
    else:
        val = weather.get(parts[0])

    if val is None:
        return False

    op = OPS.get(cond.operator)
    if op is None:
        return False

    try:
        return op(float(val), float(cond.value))
    except Exception:
        return False


def _activity_aliases(value: str):
    v = (value or "").lower().strip()
    if not v:
        return set()

    normalized = re.sub(r"[^a-z0-9]+", " ", v).strip()
    aliases = {normalized}
    if not normalized:
        return aliases

    for canonical, forms in ACTIVITY_ALIASES.items():
        if normalized in forms or any(form in normalized for form in forms):
            aliases.update(forms)
            aliases.add(canonical)

    if normalized.endswith("ing"):
        aliases.add(normalized[:-3])
        aliases.add(normalized[:-3] + "e")
    if normalized.endswith("s") and not normalized.endswith("ss"):
        aliases.add(normalized[:-1])
    if normalized.endswith("er"):
        aliases.add(normalized[:-2])
    if " " in normalized:
        aliases.add(normalized.replace(" ", ""))
    return aliases


def sop_matches(sop: SOP, weather: Dict[str, Any], intent: Dict[str, Any]) -> bool:
    # Activity matching (fuzzy, but deterministic) by comparing normalized aliases.
    act = intent.get("activity")
    if sop.activities:
        if not act:
            return False
        act_aliases = _activity_aliases(act)
        if not any(
            alias in act_aliases
            for a in sop.activities
            for alias in _activity_aliases(a)
        ):
            return False

    # group
    grp = intent.get("group")
    if sop.groups:
        if not grp:
            # allow match if group unspecified? treat as non-match
            return False
        if not any(g.lower() in grp.lower() or grp.lower() in g.lower() for g in sop.groups):
            return False

    # conditions
    for cond in sop.conditions:
        if not evaluate_condition(cond, weather, intent):
            return False

    return True


def sop_targets_intent(sop: SOP, intent: Dict[str, Any]) -> bool:
    """Return True if the SOP is relevant to the given intent by activity/group or is global.
    This does NOT evaluate weather conditions.
    """
    act = intent.get("activity")
    grp = intent.get("group")

    # If SOP lists activities, require activity to match
    if sop.activities:
        if not act:
            return False
        act_aliases = _activity_aliases(act)
        if any(
            alias in act_aliases
            for a in sop.activities
            for alias in _activity_aliases(a)
        ):
            return True
        return False

    # If SOP lists groups, require group to match
    if sop.groups:
        if not grp:
            return False
        if any(g.lower() in grp.lower() or grp.lower() in g.lower() for g in sop.groups):
            return True
        return False

    # If neither activities nor groups are specified, treat as global (applies to all intents)
    return True


def rank_sops(sops: List[SOP]) -> List[SOP]:
    return sorted(sops, key=lambda s: (-severity_value(s.severity), -s.priority))


def severity_value(s: str) -> int:
    mapping = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}
    return mapping.get(s.upper(), 0)
