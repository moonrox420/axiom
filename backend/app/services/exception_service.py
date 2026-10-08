from __future__ import annotations

import logging
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.exception import Exception as ExceptionModel
from app.models.invoice import Invoice
from app.models.asset import Asset

logger = logging.getLogger(__name__)


class ExceptionService:
    @staticmethod
    def scan_exceptions(db: Session, team_id: UUID) -> list[ExceptionModel]:
        exceptions: list[ExceptionModel] = []

        invoices = db.query(Invoice).filter(Invoice.team_id == team_id).all()
        for invoice in invoices:
            if invoice.status == "exception":
                continue

            if not invoice.client_id:
                exc = ExceptionModel(
                    team_id=team_id,
                    entity_type="invoice",
                    entity_id=invoice.id,
                    reason="Invoice is missing a valid client record.",
                    severity="high",
                    evidence=[],
                )
                db.add(exc)
                exceptions.append(exc)

            if invoice.total <= Decimal("0"):
                exc = ExceptionModel(
                    team_id=team_id,
                    entity_type="invoice",
                    entity_id=invoice.id,
                    reason="Invoice total is zero or negative.",
                    severity="high",
                    evidence=[],
                )
                db.add(exc)
                exceptions.append(exc)

        assets = db.query(Asset).filter(Asset.team_id == team_id).all()
        for asset in assets:
            if asset.confidence < 0.6:
                exc = ExceptionModel(
                    team_id=team_id,
                    entity_type="asset",
                    entity_id=asset.id,
                    reason="Location confidence is below acceptable threshold.",
                    severity="medium",
                    evidence=asset.evidence,
                )
                db.add(exc)
                exceptions.append(exc)

            if asset.status == "missing" and not asset.confidence > 0.9:
                exc = ExceptionModel(
                    team_id=team_id,
                    entity_type="asset",
                    entity_id=asset.id,
                    reason="Asset marked missing with low confidence.",
                    severity="critical",
                    evidence=asset.evidence,
                )
                db.add(exc)
                exceptions.append(exc)

        db.commit()
        logger.info(f"Scanned {len(exceptions)} exceptions for team {team_id}")
        return exceptions

    @staticmethod
    def get_exception_queue(
        db: Session,
        team_id: UUID,
        status: str = "open",
        severity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExceptionModel]:
        query = db.query(ExceptionModel).filter(
            ExceptionModel.team_id == team_id,
            ExceptionModel.status == status,
        )
        if severity:
            query = query.filter(ExceptionModel.severity == severity)
        return query.order_by(ExceptionModel.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def resolve_exception(
        db: Session,
        team_id: UUID,
        exception_id: UUID,
        resolution_notes: str = "",
    ) -> Optional[ExceptionModel]:
        exc = db.query(ExceptionModel).filter(
            ExceptionModel.id == exception_id,
            ExceptionModel.team_id == team_id,
        ).first()
        
        if not exc:
            return None

        exc.status = "resolved"
        exc.resolution_notes = resolution_notes
        db.commit()
        db.refresh(exc)
        logger.info(f"Resolved exception {exception_id}")
        return exc