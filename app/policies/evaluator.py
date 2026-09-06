from typing import List, Dict, Any
from .models import SOP
import operator

OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
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
    aliases = {v}
    if v.endswith("ing"):
        aliases.add(v[:-3])
        aliases.add(v[:-3] + "e")
    if v.endswith("s") and not v.endswith("ss"):
        aliases.add(v[:-1])
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


def rank_sops(sops: List[SOP]) -> List[SOP]:
    return sorted(sops, key=lambda s: (-severity_value(s.severity), -s.priority))


def severity_value(s: str) -> int:
    mapping = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}
    return mapping.get(s.upper(), 0)
