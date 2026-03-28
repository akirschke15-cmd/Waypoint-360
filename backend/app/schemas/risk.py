from pydantic import BaseModel, ConfigDict
from typing import Optional


class RiskCreate(BaseModel):
    workstream_id: int
    description: str
    severity: str = "medium"
    likelihood: str = "medium"
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    owner_id: Optional[int] = None
    category: Optional[str] = None


class RiskUpdate(BaseModel):
    description: Optional[str] = None
    severity: Optional[str] = None
    likelihood: Optional[str] = None
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None
    category: Optional[str] = None


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workstream_id: int
    description: str
    severity: str
    likelihood: str
    impact: Optional[str] = None
    mitigation: Optional[str] = None
    status: str
    owner_id: Optional[int] = None
    category: Optional[str] = None
