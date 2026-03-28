from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class WorkstreamStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BLOCKED = "blocked"
    COMPLETE = "complete"


class Workstream(TimestampMixin, Base):
    __tablename__ = "workstreams"

    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    purpose = Column(Text)
    scope_in = Column(Text)  # What's in scope
    scope_out = Column(Text)  # What's explicitly out
    owner_id = Column(Integer, ForeignKey("people.id"), nullable=True)
    status = Column(SAEnum(WorkstreamStatus), default=WorkstreamStatus.NOT_STARTED)
    sort_order = Column(Integer, default=0)

    # Baseline scope for scope creep detection
    baseline_scope = Column(Text)  # Snapshot of original scope at Align gate

    # Relationships
    program = relationship("Program", back_populates="workstreams")
    owner = relationship("Person", back_populates="owned_workstreams", foreign_keys=[owner_id])
    deliverables = relationship("Deliverable", back_populates="workstream", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="workstream", cascade="all, delete-orphan")
    decisions = relationship("Decision", back_populates="workstream", cascade="all, delete-orphan")
    status_updates = relationship("StatusUpdate", back_populates="workstream", cascade="all, delete-orphan")
    scope_changes = relationship("ScopeChange", back_populates="workstream", cascade="all, delete-orphan")

    # Dependencies where this workstream is the source (needs something)
    outbound_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.source_workstream_id",
        back_populates="source_workstream",
        cascade="all, delete-orphan",
    )
    # Dependencies where this workstream is the target (provides something)
    inbound_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.target_workstream_id",
        back_populates="target_workstream",
    )
    # Team members
    members = relationship("Person", back_populates="workstream", foreign_keys="Person.workstream_id")
