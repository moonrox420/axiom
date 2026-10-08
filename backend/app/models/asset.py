from __future__ import annotations

from sqlalchemy import Column, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Asset(Base, IDMixin, TimestampMixin):
    __tablename__ = "assets"

    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String(50), default="in_service")
    current_location = Column(String(500), nullable=False)
    confidence = Column(Float, default=0.8)
    notes = Column(Text, nullable=True)
    evidence = Column(JSONB, default=[], nullable=False)
    metadata = Column(JSONB, default={}, nullable=False)

    team = relationship("Team", back_populates="assets")
    location_events = relationship(
        "AssetLocationEvent", back_populates="asset", cascade="all, delete-orphan"
    )


class AssetLocationEvent(Base, IDMixin, TimestampMixin):
    __tablename__ = "asset_location_events"

    asset_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    location = Column(String(500), nullable=False)
    source = Column(String(100), nullable=False)
    confidence = Column(Float, default=0.8)
    evidence = Column(Text, nullable=True)
    metadata = Column(JSONB, default={}, nullable=False)

    asset = relationship("Asset", back_populates="location_events")
