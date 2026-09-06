import yaml
from typing import List
from .models import SOP
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


def load_sops(path: str) -> List[SOP]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    sops = []
    for item in data.get("sops", []):
        try:
            s = SOP(**item)
            sops.append(s)
        except ValidationError as e:
            logger.exception("Invalid SOP: %s", item.get("id"))
            raise

    return sops
