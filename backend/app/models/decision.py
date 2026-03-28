from sqlalchemy import Column, String, Text, Integer, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class DecisionStatus(str, enum.Enum):
    NEEDED = "needed"
    PENDING = "pending"
    MADE = "made"
    DEFERRED = "deferred"


class Decision(TimestampMixin, Base):
    __tablename__ = "decisions"

    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=True)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(DecisionStatus), default=DecisionStatus.NEEDED)
    decision_maker = Column(String(255))
    due_date = Column(Date)
    resolution = Column(Text)
    decided_at = Column(DateTime, nullable=True)
    impact = Column(Text)  # What happens if this decision is delayed

    # Relationships
    workstream = relationship("Workstream", back_populates="decisions")
    gate = relationship("Gate", back_populates="decisions")
