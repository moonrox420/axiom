from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdate
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.post("", response_model=InvoiceRead)
def create_invoice(
    team_id: UUID,
    created_by_id: UUID,
    payload: InvoiceCreate,
    db: Session = Depends(get_db),
):
    return InvoiceService.create_invoice(db, team_id, created_by_id, payload)


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    team_id: UUID,
    invoice_id: UUID,
    db: Session = Depends(get_db),
):
    invoice = InvoiceService.get_invoice(db, team_id, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice


@router.get("", response_model=list[InvoiceRead])
def list_invoices(
    team_id: UUID,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return InvoiceService.list_invoices(db, team_id, status, skip, limit)


@router.put("/{invoice_id}", response_model=InvoiceRead)
def update_invoice(
    team_id: UUID,
    invoice_id: UUID,
    payload: InvoiceUpdate,
    db: Session = Depends(get_db),
):
    invoice = InvoiceService.update_invoice(db, team_id, invoice_id, payload)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found",
        )
    return invoice
