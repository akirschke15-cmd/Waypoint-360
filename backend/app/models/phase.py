from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class Phase(TimestampMixin, Base):
    __tablename__ = "phases"

    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    name = Column(String(100), nullable=False)  # Align, Incept, Deliver
    description = Column(Text)
    start_week = Column(Integer, nullable=False)
    end_week = Column(Integer)
    goal = Column(Text)
    key_activities = Column(Text)
    exit_criteria = Column(Text)
    sort_order = Column(Integer, default=0)

    # Relationships
    program = relationship("Program", back_populates="phases")
    gates = relationship("Gate", back_populates="phase")
