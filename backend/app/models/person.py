from sqlalchemy import Column, String, Integer, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OWNER = "owner"  # Workstream owner
    VIEWER = "viewer"  # Leadership, read-only


class Person(TimestampMixin, Base):
    __tablename__ = "people"

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    role = Column(SAEnum(UserRole), default=UserRole.VIEWER)
    title = Column(String(255))
    team = Column(String(255))
    organization = Column(String(255))  # e.g., "ProServ", "SWA", "TBD"
    capacity_pct = Column(Float, default=100.0)  # % allocated to Waypoint
    workstream_id = Column(Integer, ForeignKey("workstreams.id"), nullable=True)

    # Auth
    hashed_password = Column(String(255))

    # Relationships
    workstream = relationship("Workstream", back_populates="members", foreign_keys=[workstream_id])
    owned_workstreams = relationship("Workstream", back_populates="owner", foreign_keys="Workstream.owner_id")
    assigned_deliverables = relationship("Deliverable", back_populates="assignee")
    owned_risks = relationship("Risk", back_populates="owner")
    status_updates = relationship("StatusUpdate", back_populates="author")
