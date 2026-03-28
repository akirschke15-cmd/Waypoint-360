from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class ChangeType(str, enum.Enum):
    ADDITION = "addition"
    REMOVAL = "removal"
    MODIFICATION = "modification"


class FlaggedBy(str, enum.Enum):
    USER = "user"
    AI = "ai"


class ScopeChange(TimestampMixin, Base):
    __tablename__ = "scope_changes"

    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    description = Column(Text, nullable=False)
    change_type = Column(SAEnum(ChangeType), nullable=False)
    baseline_scope = Column(Text)
    current_scope = Column(Text)
    flagged_by = Column(SAEnum(FlaggedBy), default=FlaggedBy.USER)
    flagged_at = Column(DateTime)
    resolution = Column(Text)

    # Relationships
    workstream = relationship("Workstream", back_populates="scope_changes")
