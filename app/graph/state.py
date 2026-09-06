from typing import Optional, Dict, Any
from pydantic import BaseModel


class SessionState(BaseModel):
    session_id: str
    raw_input: str
    intent: Dict[str, Any] = {}
    location: Optional[Dict[str, Any]] = None
    weather: Optional[Dict[str, Any]] = None
    matched_sops: list = []
    selected_sop: Optional[Dict[str, Any]] = None
    decision: Optional[Dict[str, Any]] = None
