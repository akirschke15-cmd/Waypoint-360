from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class DeliverableCreate(BaseModel):
    workstream_id: int
    gate_id: int
    name: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class DeliverableUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class DeliverableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workstream_id: int
    gate_id: int
    name: str
    description: Optional[str] = None
    status: str
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None
