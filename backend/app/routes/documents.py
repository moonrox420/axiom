from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.document import DocumentRead
from app.services.document_service import DocumentService

router = APIRouter()


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    team_id: UUID,
    owner_id: UUID,
    source_type: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    try:
        document = DocumentService.upload_document(
            db,
            team_id,
            owner_id,
            file.filename or "document",
            content,
            source_type,
        )
        return document
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload failed: {exc!s}",
        )


@router.post("/{document_id}/process", response_model=DocumentRead)
def process_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    try:
        return DocumentService.process_document(db, document_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Processing failed: {exc!s}",
        )
