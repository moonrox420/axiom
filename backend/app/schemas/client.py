from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    payment_terms_days: str = "net_14"
    notes: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    tax_id: str | None = None
    payment_terms_days: str | None = None
    notes: str | None = None


class ClientRead(ClientBase):
    id: UUID
    team_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True