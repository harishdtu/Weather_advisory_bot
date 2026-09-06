from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class Condition(BaseModel):
    # simple condition schema
    name: str
    field: str
    operator: str
    value: Any


class SOP(BaseModel):
    id: str
    name: str
    category: Optional[str]
    severity: str
    description: Optional[str] = None
    conditions: List[Condition] = Field(default_factory=list)
    activities: List[str] = Field(default_factory=list)
    groups: List[str] = Field(default_factory=list)
    guidance: Optional[str] = None
    priority: int = 50
    fuzzy: Optional[bool] = False
    source: Optional[str] = None
    version: Optional[str] = None
