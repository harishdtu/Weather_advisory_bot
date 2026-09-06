import os
import re
from typing import Dict, Optional
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def parse_intent_simple(text: str) -> Dict[str, Optional[str]]:
    # simple heuristic parser
    text_l = text.lower()
    # activity detection
    activities = ["cycle", "cycling", "bike", "run", "jog", "picnic", "picnicking", "walk", "hike", "travel", "commute", "park", "play"]
    activity = None
    for a in activities:
        if a in text_l:
            activity = a
            break

    # group detection
    groups = ["child", "children", "kid", "elderly", "pet", "pets", "dog"]
    group = None
    for g in groups:
        if g in text_l:
            group = g
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
