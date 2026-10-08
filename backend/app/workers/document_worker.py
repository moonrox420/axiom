from __future__ import annotations

import logging
from uuid import UUID

from app.core.database import SessionLocal
from app.services.document_service import DocumentService

from .celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str) -> dict:
    db = SessionLocal()
    try:
        result = DocumentService.process_document(db, UUID(document_id))
        logger.info(f"Processed document {document_id}")
        return {
            "status": "success",
            "document_id": document_id,
            "confidence": result.confidence,
        }
    except Exception as exc:
        logger.error(f"Failed to process document {document_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)
    finally:
        db.close()