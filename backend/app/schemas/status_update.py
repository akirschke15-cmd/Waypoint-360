from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class StatusUpdateCreate(BaseModel):
    workstream_id: int
    gate_id: Optional[int] = None
    content: str
    status_color: str = "green"


class StatusUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workstream_id: int
    gate_id: Optional[int] = None
    author_id: Optional[int] = None
    content: str
    status_color: str
    created_at: datetime
