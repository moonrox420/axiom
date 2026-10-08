from __future__ import annotations

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Exception(Base, IDMixin, TimestampMixin):
    __tablename__ = "exceptions"
    
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    assigned_to_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    reason = Column(String(500), nullable=False)
    severity = Column(String(20), default="medium", index=True)
    status = Column(String(50), default="open", index=True)
    resolution_notes = Column(Text, nullable=True)
    evidence = Column(JSONB, default=[], nullable=False)
    
    assigned_to_user = relationship("User", back_populates="exceptions")


class AuditLog(Base, IDMixin, TimestampMixin):
    __tablename__ = "audit_logs"
    
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    changes = Column(JSONB, default={}, nullable=False)
    ip_address = Column(String(50), nullable=True)