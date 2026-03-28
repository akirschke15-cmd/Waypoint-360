from sqlalchemy import Column, String, Text, Date, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class ProgramStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETE = "complete"


class Program(TimestampMixin, Base):
    __tablename__ = "programs"

    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(SAEnum(ProgramStatus), default=ProgramStatus.ACTIVE)

    # Relationships
    phases = relationship("Phase", back_populates="program", cascade="all, delete-orphan")
    gates = relationship("Gate", back_populates="program", cascade="all, delete-orphan")
    workstreams = relationship("Workstream", back_populates="program", cascade="all, delete-orphan")
