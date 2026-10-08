from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.exception_service import ExceptionService

router = APIRouter()


@router.post("/scan")
def scan_exceptions(
    team_id: UUID,
    db: Session = Depends(get_db),
):
    exceptions = ExceptionService.scan_exceptions(db, team_id)
    return {
        "count": len(exceptions),
        "exceptions": [
            {
                "id": str(e.id),
                "entity_type": e.entity_type,
                "entity_id": str(e.entity_id),
                "reason": e.reason,
                "severity": e.severity,
            }
            for e in exceptions
        ],
    }


@router.get("")
def get_exception_queue(
    team_id: UUID,
    status: str = "open",
    severity: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    exceptions = ExceptionService.get_exception_queue(
        db, team_id, status, severity, skip, limit
    )
    return [
        {
            "id": str(e.id),
            "entity_type": e.entity_type,
            "entity_id": str(e.entity_id),
            "reason": e.reason,
            "severity": e.severity,
            "status": e.status,
            "evidence": e.evidence,
            "created_at": e.created_at.isoformat(),
        }
        for e in exceptions
    ]


@router.post("/{exception_id}/resolve")
def resolve_exception(
    team_id: UUID,
    exception_id: UUID,
    resolution_notes: str = "",
    db: Session = Depends(get_db),
):
    exc = ExceptionService.resolve_exception(db, team_id, exception_id, resolution_notes)
    if not exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exception not found",
        )
    return {
        "id": str(exc.id),
        "status": exc.status,
        "resolution_notes": exc.resolution_notes,
    }