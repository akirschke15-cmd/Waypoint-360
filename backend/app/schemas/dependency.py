from pydantic import BaseModel, ConfigDict
from typing import Optional


class DependencyCreate(BaseModel):
    source_workstream_id: int
    target_workstream_id: int
    gate_id: Optional[int] = None
    description: str
    dep_type: str = "needs_from"
    criticality: str = "medium"
    notes: Optional[str] = None


class DependencyUpdate(BaseModel):
    description: Optional[str] = None
    dep_type: Optional[str] = None
    status: Optional[str] = None
    criticality: Optional[str] = None
    notes: Optional[str] = None


class DependencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_workstream_id: int
    target_workstream_id: int
    gate_id: Optional[int] = None
    description: str
    dep_type: str
    status: str
    criticality: str
    notes: Optional[str] = None
