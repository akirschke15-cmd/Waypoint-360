from pydantic import BaseModel, ConfigDict
from typing import Optional


class WorkstreamCreate(BaseModel):
    program_id: int
    name: str
    short_name: Optional[str] = None
    purpose: Optional[str] = None
    scope_in: Optional[str] = None
    scope_out: Optional[str] = None
    owner_id: Optional[int] = None
    status: str = "not_started"


class WorkstreamUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    purpose: Optional[str] = None
    scope_in: Optional[str] = None
    scope_out: Optional[str] = None
    owner_id: Optional[int] = None
    status: Optional[str] = None


class WorkstreamSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    short_name: Optional[str] = None
    purpose: Optional[str] = None
    status: Optional[str] = None
