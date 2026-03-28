from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ScopeChangeCreate(BaseModel):
    workstream_id: int
    description: str
    change_type: str
    baseline_scope: Optional[str] = None
    current_scope: Optional[str] = None
    flagged_by: str = "user"


class ScopeChangeUpdate(BaseModel):
    resolution: Optional[str] = None
    description: Optional[str] = None
    current_scope: Optional[str] = None


class ScopeChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workstream_id: int
    description: str
    change_type: str
    baseline_scope: Optional[str] = None
    current_scope: Optional[str] = None
    flagged_by: str
    flagged_at: Optional[datetime] = None
    resolution: Optional[str] = None
