from __future__ import annotations

from decimal import Decimal
from sqlalchemy import (
    Column,
    Date,
    DECIMAL,
    Enum,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Invoice(Base, IDMixin, TimestampMixin):
    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint("team_id", "invoice_number", name="uq_invoice_team_number"),
    )
    
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_by_id = Column(UUID(as_uuid=True), nullable=True)
    invoice_number = Column(String(50), nullable=False, index=True)
    issue_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    status = Column(String(50), default="draft", nullable=False, index=True)
    currency = Column(String(3), default="USD")
    
    subtotal = Column(DECIMAL(19, 2), default=Decimal("0"), nullable=False)
    tax_amount = Column(DECIMAL(19, 2), default=Decimal("0"), nullable=False)
    tax_rate = Column(DECIMAL(5, 4), default=Decimal("0.0825"))
    freight = Column(DECIMAL(19, 2), default=Decimal("0"))
    discount = Column(DECIMAL(19, 2), default=Decimal("0"))
    total = Column(DECIMAL(19, 2), default=Decimal("0"), nullable=False)
    
    notes = Column(Text, nullable=True)
    evidence = Column(JSONB, default=[], nullable=False)
    
    client = relationship("Client", back_populates="invoices")
    created_by_user = relationship("User", back_populates="invoices")
    team = relationship("Team", back_populates="invoices")
    line_items = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")
    documents = relationship("Document", secondary="invoice_documents", back_populates="invoices")
    expenses = relationship("Expense", back_populates="invoice")
    payments = relationship("Payment", back_populates="invoice")


class LineItem(Base, IDMixin):
    __tablename__ = "line_items"
    
    invoice_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    description = Column(String(500), nullable=False)
    quantity = Column(DECIMAL(19, 4), nullable=False)
    unit_cost = Column(DECIMAL(19, 2), nullable=False)
    tax_rate = Column(DECIMAL(5, 4), nullable=False)
    category = Column(String(50), default="service")
    freight = Column(DECIMAL(19, 2), default=Decimal("0"))
    notes = Column(String(500), nullable=True)
    
    invoice = relationship("Invoice", back_populates="line_items")


class InvoiceDocument(Base):
    __tablename__ = "invoice_documents"
    
    invoice_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    document_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)