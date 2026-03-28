from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class DeliverableStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"


class Deliverable(TimestampMixin, Base):
    __tablename__ = "deliverables"

    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SAEnum(DeliverableStatus), default=DeliverableStatus.NOT_STARTED)
    due_date = Column(Date)
    assignee_id = Column(Integer, ForeignKey("people.id"), nullable=True)

    # Relationships
    workstream = relationship("Workstream", back_populates="deliverables")
    gate = relationship("Gate", back_populates="deliverables")
    assignee = relationship("Person", back_populates="assigned_deliverables")
