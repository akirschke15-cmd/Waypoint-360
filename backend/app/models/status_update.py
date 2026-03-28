from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class StatusColor(str, enum.Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class StatusUpdate(TimestampMixin, Base):
    __tablename__ = "status_updates"

    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    content = Column(Text, nullable=False)
    status_color = Column(SAEnum(StatusColor), default=StatusColor.GREEN)

    # Relationships
    workstream = relationship("Workstream", back_populates="status_updates")
    author = relationship("Person", back_populates="status_updates")
