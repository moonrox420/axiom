from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.asset_service import AssetService

router = APIRouter()


class RegisterAssetRequest:
    name: str
    category: str
    location: str
    source: str
    confidence: float = 0.8
    status: str = "in_service"


class UpdateAssetLocationRequest:
    location: str
    source: str
    confidence: float = 0.8
    evidence: str = ""


@router.post("/register")
def register_asset(
    team_id: UUID,
    name: str,
    category: str,
    location: str,
    source: str,
    confidence: float = 0.8,
    status: str = "in_service",
    db: Session = Depends(get_db),
):
    asset = AssetService.register_asset(
        db, team_id, name, category, location, source, confidence, status
    )
    return {
        "id": str(asset.id),
        "name": asset.name,
        "category": asset.category,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": asset.confidence,
    }


@router.post("/{asset_id}/location")
def update_asset_location(
    team_id: UUID,
    asset_id: UUID,
    location: str,
    source: str,
    confidence: float = 0.8,
    evidence: str = "",
    db: Session = Depends(get_db),
):
    asset = AssetService.update_asset_location(
        db, team_id, asset_id, location, source, confidence, evidence
    )
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return {
        "id": str(asset.id),
        "name": asset.name,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": asset.confidence,
    }


@router.get("/{asset_id}")
def get_asset(
    team_id: UUID,
    asset_id: UUID,
    db: Session = Depends(get_db),
):
    asset = AssetService.get_asset(db, team_id, asset_id)
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    return {
        "id": str(asset.id),
        "name": asset.name,
        "category": asset.category,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": asset.confidence,
        "evidence": asset.evidence,
    }


@router.get("")
def list_assets(
    team_id: UUID,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    assets = AssetService.list_assets(db, team_id, status, skip, limit)
    return [
        {
            "id": str(a.id),
            "name": a.name,
            "category": a.category,
            "current_location": a.current_location,
            "status": a.status,
            "confidence": a.confidence,
        }
        for a in assets
    ]


@router.get("/{asset_id}/history")
def get_asset_history(
    team_id: UUID,
    asset_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    history = AssetService.get_asset_history(db, team_id, asset_id, limit)
    return [
        {
            "id": str(event.id),
            "asset_id": str(event.asset_id),
            "location": event.location,
            "source": event.source,
            "confidence": event.confidence,
            "observed_at": event.created_at.isoformat(),
        }
        for event in history
    ]
