from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceCreate, InvoiceLineItemCreate
from app.services.invoice_service import InvoiceService
from .celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def generate_invoice_from_document_task(
    self, document_id: str, client_id: str, team_id: str, created_by_id: str
) -> dict:
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == UUID(document_id)).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        line_items = []
        if document.extracted_data and document.extracted_data.get("amounts"):
            for amount_data in document.extracted_data["amounts"]:
                line_items.append(
                    InvoiceLineItemCreate(
                        description="Service",
                        quantity=1,
                        unit_cost=amount_data["amount"],
                        tax_rate=0.0825,
                        category="service",
                    )
                )

        if not line_items:
            line_items.append(
                InvoiceLineItemCreate(
                    description="General service",
                    quantity=1,
                    unit_cost=0,
                    tax_rate=0.0825,
                )
            )

        invoice_create = InvoiceCreate(
            client_id=UUID(client_id),
            issue_date=date.today(),
            due_date=date.today(),
            line_items=line_items,
        )

        invoice = InvoiceService.create_invoice(
            db, UUID(team_id), UUID(created_by_id), invoice_create
        )

        logger.info(f"Generated invoice {invoice.id} from document {document_id}")
        return {
            "status": "success",
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "total": str(invoice.total),
        }
    except Exception as exc:
        logger.error(f"Failed to generate invoice from document {document_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()