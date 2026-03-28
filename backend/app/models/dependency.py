from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class DependencyType(str, enum.Enum):
    NEEDS_FROM = "needs_from"  # Source needs something from target
    PROVIDES_TO = "provides_to"  # Source provides something to target
    BLOCKS = "blocks"  # Source blocks target until resolved
    INFORMS = "informs"  # Source informs target (non-blocking)


class DependencyStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    BLOCKED = "blocked"
    AT_RISK = "at_risk"


class Criticality(str, enum.Enum):
    CRITICAL = "critical"  # On critical path, delay cascades
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Dependency(TimestampMixin, Base):
    __tablename__ = "dependencies"

    source_workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    target_workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=False)
    gate_id = Column(Integer, ForeignKey("gates.id"), nullable=True)  # Which gate this dependency is relevant to
    description = Column(Text, nullable=False)
    dep_type = Column(SAEnum(DependencyType), default=DependencyType.NEEDS_FROM)
    status = Column(SAEnum(DependencyStatus), default=DependencyStatus.OPEN)
    criticality = Column(SAEnum(Criticality), default=Criticality.MEDIUM)
    notes = Column(Text)

    # Relationships
    source_workstream = relationship("Workstream", foreign_keys=[source_workstream_id], back_populates="outbound_dependencies")
    target_workstream = relationship("Workstream", foreign_keys=[target_workstream_id], back_populates="inbound_dependencies")
    gate = relationship("Gate", back_populates="dependencies")
