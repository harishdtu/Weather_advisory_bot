import os
import re
from typing import Dict, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


ACTIVITY_ALIASES = {
    "run": {"run", "running", "runner", "jog", "jogging", "exercise", "outdoor exercise", "workout"},
    "cycle": {"cycle", "cycling", "bicycle", "bike", "biking", "ride", "riding", "cyclist"},
    "walk": {"walk", "walking", "hike", "hiking", "hiker", "trek", "trekking", "stroll", "strolling"},
    "picnic": {"picnic", "picnicking", "outdoor meal"},
    "travel": {"travel", "commute", "drive", "driving", "trip"},
    "park": {"park", "play", "playing", "playground"},
    "pets": {"pet", "pets", "dog", "dog walk", "walk dog"},
}

GROUP_ALIASES = {
    "children": {"child", "children", "kid", "kids"},
    "elderly": {"elderly", "old", "senior", "seniors"},
    "pets": {"pet", "pets", "dog", "dogs"},
}


def parse_intent_simple(text: str) -> Dict[str, Optional[str]]:
    # simple heuristic parser
    text_l = text.lower()
    # activity detection: map any known alias (word-boundary match)
    activity = None
    # build alias -> canonical map
    alias_map = {}
    for canonical, aliases in ACTIVITY_ALIASES.items():
        for a in aliases:
            alias_map[a] = canonical

    # sort aliases by length to prefer multi-word or longer matches
    sorted_aliases = sorted(alias_map.keys(), key=lambda s: -len(s))
    for alias in sorted_aliases:
        # match as whole word or phrase
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text_l):
            activity = alias_map[alias]
            break

    # group detection: normalize to canonical group names
    group = None
    for canonical, aliases in GROUP_ALIASES.items():
        for a in aliases:
            pattern = r"\b" + re.escape(a) + r"\b"
            if re.search(pattern, text_l):
                group = canonical
                break
        if group:
            break

    # time detection
    time = None
    m = re.search(r"(this|today|tonight|evening|morning|afternoon)", text_l)
    if m:
        time = m.group(1)

    # location naive extraction: look for 'in {city}' or 'at {city}'
    loc = None
    m = re.search(r"\b(in|at|near) ([A-Za-z][A-Za-z\s'-]*)[?.,!]?\s*$", text.strip(), re.IGNORECASE)
    if m:
        loc = m.group(2).strip().rstrip("?.!,")

    return {
        "activity": activity,
        "group": group,
        "time": time,
        "location": loc,
        "raw": text,
    }
