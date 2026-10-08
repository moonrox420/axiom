from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class IDMixin:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)