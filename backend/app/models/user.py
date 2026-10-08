from __future__ import annotations

from sqlalchemy import Boolean, Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_user_email"),)
    
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    teams = relationship("Team", secondary="team_members", back_populates="users")
    documents = relationship("Document", back_populates="owner")
    invoices = relationship("Invoice", back_populates="created_by_user")
    exceptions = relationship("Exception", back_populates="assigned_to_user")


class Team(Base, IDMixin, TimestampMixin):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("slug", name="uq_team_slug"),)
    
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    description = Column(String(1000), nullable=True)
    
    users = relationship("User", secondary="team_members", back_populates="teams")
    clients = relationship("Client", back_populates="team")
    invoices = relationship("Invoice", back_populates="team")
    assets = relationship("Asset", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"
    
    team_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, index=True)
    role = Column(String(50), default="member", nullable=False)