from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class InvoiceLineItemCreate(BaseModel):
    description: str
    quantity: Decimal
    unit_cost: Decimal
    tax_rate: Decimal
    category: str = "service"
    freight: Decimal = Decimal("0")
    notes: str | None = None


class InvoiceLineItemRead(InvoiceLineItemCreate):
    id: UUID

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    issue_date: date
    due_date: date
    notes: str | None = None


class InvoiceCreate(InvoiceBase):
    client_id: UUID
    line_items: list[InvoiceLineItemCreate] = []


class InvoiceUpdate(BaseModel):
    issue_date: date | None = None
    due_date: date | None = None
    status: str | None = None
    notes: str | None = None
    line_items: list[InvoiceLineItemCreate] | None = None


class InvoiceRead(InvoiceBase):
    id: UUID
    team_id: UUID
    client_id: UUID
    invoice_number: str
    status: str
    currency: str
    subtotal: Decimal
    tax_amount: Decimal
    tax_rate: Decimal
    freight: Decimal
    discount: Decimal
    total: Decimal
    line_items: list[InvoiceLineItemRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True