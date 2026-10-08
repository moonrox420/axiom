from __future__ import annotations

from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Client(Base, IDMixin, TimestampMixin):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("team_id", "email", name="uq_client_team_email"),
        UniqueConstraint("team_id", "name", name="uq_client_team_name"),
    )

    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(1000), nullable=True)
    tax_id = Column(String(50), nullable=True)
    payment_terms_days = Column(String(50), default="net_14")
    notes = Column(String(1000), nullable=True)

    team = relationship("Team", back_populates="clients")
    invoices = relationship("Invoice", back_populates="client")
    contracts = relationship("Contract", back_populates="client")
