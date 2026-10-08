from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.invoice import Invoice, LineItem
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceUpdate

logger = logging.getLogger(__name__)


class InvoiceService:
    @staticmethod
    def generate_invoice_number(db: Session, team_id: UUID) -> str:
        today = datetime.now(timezone.utc).date()
        count = db.query(Invoice).filter(
            Invoice.team_id == team_id,
            Invoice.issue_date >= date(today.year, today.month, 1),
        ).count()
        return f"AX-{today.strftime('%Y%m%d')}-{count + 1:04d}"

    @staticmethod
    def create_invoice(
        db: Session, team_id: UUID, created_by_id: UUID, payload: InvoiceCreate
    ) -> InvoiceRead:
        invoice_number = InvoiceService.generate_invoice_number(db, team_id)
        
        invoice = Invoice(
            team_id=team_id,
            client_id=payload.client_id,
            created_by_id=created_by_id,
            invoice_number=invoice_number,
            issue_date=payload.issue_date,
            due_date=payload.due_date,
            status="draft",
            currency=settings.default_currency,
            tax_rate=Decimal(str(settings.default_tax_rate)),
            notes=payload.notes,
        )

        db.add(invoice)
        db.flush()

        for item_data in payload.line_items:
            line_item = LineItem(
                invoice_id=invoice.id,
                description=item_data.description,
                quantity=item_data.quantity,
                unit_cost=item_data.unit_cost,
                tax_rate=item_data.tax_rate,
                category=item_data.category,
                freight=item_data.freight,
                notes=item_data.notes,
            )
            db.add(line_item)

        db.commit()
        db.refresh(invoice)
        InvoiceService._recalculate_totals(db, invoice)
        logger.info(f"Created invoice {invoice.id} for team {team_id}")
        return InvoiceRead.from_orm(invoice)

    @staticmethod
    def get_invoice(db: Session, team_id: UUID, invoice_id: UUID) -> InvoiceRead | None:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.team_id == team_id,
        ).first()
        return InvoiceRead.from_orm(invoice) if invoice else None

    @staticmethod
    def list_invoices(
        db: Session, team_id: UUID, status: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[InvoiceRead]:
        query = db.query(Invoice).filter(Invoice.team_id == team_id)
        if status:
            query = query.filter(Invoice.status == status)
        invoices = query.offset(skip).limit(limit).all()
        return [InvoiceRead.from_orm(inv) for inv in invoices]

    @staticmethod
    def update_invoice(
        db: Session, team_id: UUID, invoice_id: UUID, payload: InvoiceUpdate
    ) -> InvoiceRead | None:
        invoice = db.query(Invoice).filter(
            Invoice.id == invoice_id,
            Invoice.team_id == team_id,
        ).first()
        
        if not invoice:
            return None

        if payload.issue_date is not None:
            invoice.issue_date = payload.issue_date
        if payload.due_date is not None:
            invoice.due_date = payload.due_date
        if payload.status is not None:
            invoice.status = payload.status
        if payload.notes is not None:
            invoice.notes = payload.notes

        if payload.line_items is not None:
            db.query(LineItem).filter(LineItem.invoice_id == invoice_id).delete()
            for item_data in payload.line_items:
                line_item = LineItem(
                    invoice_id=invoice.id,
                    description=item_data.description,
                    quantity=item_data.quantity,
                    unit_cost=item_data.unit_cost,
                    tax_rate=item_data.tax_rate,
                    category=item_data.category,
                    freight=item_data.freight,
                    notes=item_data.notes,
                )
                db.add(line_item)

        db.commit()
        db.refresh(invoice)
        InvoiceService._recalculate_totals(db, invoice)
        logger.info(f"Updated invoice {invoice_id}")
        return InvoiceRead.from_orm(invoice)

    @staticmethod
    def _recalculate_totals(db: Session, invoice: Invoice) -> None:
        line_items = db.query(LineItem).filter(LineItem.invoice_id == invoice.id).all()
        
        subtotal = sum(
            (item.quantity * item.unit_cost) for item in line_items
        )
        tax = sum(
            (item.quantity * item.unit_cost * item.tax_rate) for item in line_items
        )
        freight = sum((item.freight for item in line_items), Decimal(0))
        
        invoice.subtotal = subtotal
        invoice.tax_amount = tax
        invoice.freight = freight
        invoice.total = subtotal + tax + freight - (invoice.discount or Decimal(0))
        
        db.commit()
