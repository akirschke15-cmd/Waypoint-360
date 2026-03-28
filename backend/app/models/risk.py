from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Likelihood(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskStatus(str, enum.Enum):
    OPEN = "open"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class Risk(TimestampMixin, Base):
    __tablename__ = "risks"

    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SAEnum(Severity), default=Severity.MEDIUM)
    likelihood = Column(SAEnum(Likelihood), default=Likelihood.MEDIUM)
    impact = Column(Text)
    mitigation = Column(Text)
    status = Column(SAEnum(RiskStatus), default=RiskStatus.OPEN)
    owner_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    category = Column(String(100))  # technical, resourcing, dependency, timeline, scope

    # Relationships
    workstream = relationship("Workstream", back_populates="risks")
    owner = relationship("Person", back_populates="owned_risks")
