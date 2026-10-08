from __future__ import annotations

from sqlalchemy import Column, Date, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Contract(Base, IDMixin, TimestampMixin):
    __tablename__ = "contracts"

    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    terms = Column(JSONB, default={}, nullable=False)
    s3_path = Column(String(1000), nullable=True)

    client = relationship("Client", back_populates="contracts")
