from __future__ import annotations

from decimal import Decimal
from sqlalchemy import Column, Date, DECIMAL, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Expense(Base, IDMixin, TimestampMixin):
    __tablename__ = "expenses"
    
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    invoice_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    category = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(DECIMAL(19, 2), nullable=False)
    currency = Column(String(3), default="USD")
    expense_date = Column(Date, nullable=False)
    status = Column(String(50), default="pending")
    receipt_s3_path = Column(String(1000), nullable=True)
    evidence = Column(JSONB, default=[], nullable=False)
    notes = Column(Text, nullable=True)
    
    invoice = relationship("Invoice", back_populates="expenses")


class Payment(Base, IDMixin, TimestampMixin):
    __tablename__ = "payments"
    
    invoice_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    amount = Column(DECIMAL(19, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=False)
    reference_number = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")
    
    invoice = relationship("Invoice", back_populates="payments")