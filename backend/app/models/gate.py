from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class GateStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"


class Gate(TimestampMixin, Base):
    __tablename__ = "gates"

    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    phase_id = Column(Integer, ForeignKey("phases.id"), nullable=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))  # e.g., "ALIGN", "INCEPT 1"
    description = Column(Text)
    week_number = Column(Integer, nullable=False)
    due_date = Column(Date)
    status = Column(SAEnum(GateStatus), default=GateStatus.NOT_STARTED)
    sort_order = Column(Integer, default=0)

    # Relationships
    program = relationship("Program", back_populates="gates")
    phase = relationship("Phase", back_populates="gates")
    exit_criteria = relationship("GateExitCriteria", back_populates="gate", cascade="all, delete-orphan")
    deliverables = relationship("Deliverable", back_populates="gate")
    dependencies = relationship("Dependency", back_populates="gate")
    decisions = relationship("Decision", back_populates="gate")


class CriteriaStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"


class GateExitCriteria(TimestampMixin, Base):
    __tablename__ = "gate_exit_criteria"

    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(CriteriaStatus), default=CriteriaStatus.NOT_STARTED)
    notes = Column(Text)
    sort_order = Column(Integer, default=0)

    # Relationships
    gate = relationship("Gate", back_populates="exit_criteria")
