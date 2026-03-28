from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class DecisionCreate(BaseModel):
    workstream_id: int
    gate_id: Optional[int] = None
    description: str
    decision_maker: Optional[str] = None
    due_date: Optional[date] = None
    impact: Optional[str] = None


class DecisionUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    decision_maker: Optional[str] = None
    due_date: Optional[date] = None
    resolution: Optional[str] = None
    decided_at: Optional[datetime] = None
    impact: Optional[str] = None


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workstream_id: int
    gate_id: Optional[int] = None
    description: str
    status: str
    decision_maker: Optional[str] = None
    due_date: Optional[date] = None
    resolution: Optional[str] = None
    decided_at: Optional[datetime] = None
    impact: Optional[str] = None
