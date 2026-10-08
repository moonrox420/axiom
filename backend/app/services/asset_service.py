from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.asset import Asset, AssetLocationEvent

logger = logging.getLogger(__name__)


class AssetService:
    @staticmethod
    def register_asset(
        db: Session,
        team_id: UUID,
        name: str,
        category: str,
        location: str,
        source: str,
        confidence: float = 0.8,
        status: str = "in_service",
    ) -> Asset:
        asset = Asset(
            team_id=team_id,
            name=name.strip().title(),
            category=category.strip(),
            current_location=location.strip(),
            status=status,
            confidence=confidence,
            evidence=[f"{source}:{location}"],
        )
        db.add(asset)
        db.flush()

        location_event = AssetLocationEvent(
            asset_id=asset.id,
            location=location.strip(),
            source=source,
            confidence=confidence,
            evidence=f"{source}:{location}",
        )
        db.add(location_event)
        db.commit()
        db.refresh(asset)
        logger.info(f"Registered asset {asset.id} for team {team_id}")
        return asset

    @staticmethod
    def update_asset_location(
        db: Session,
        team_id: UUID,
        asset_id: UUID,
        location: str,
        source: str,
        confidence: float = 0.8,
        evidence: str = "",
    ) -> Optional[Asset]:
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.team_id == team_id,
        ).first()
        
        if not asset:
            return None

        asset.current_location = location.strip()
        asset.confidence = confidence
        asset.evidence.append(f"{source}:{location}" if not evidence else evidence)

        location_event = AssetLocationEvent(
            asset_id=asset.id,
            location=location.strip(),
            source=source,
            confidence=confidence,
            evidence=evidence or f"{source}:{location}",
        )
        db.add(location_event)
        db.commit()
        db.refresh(asset)
        logger.info(f"Updated asset {asset_id} location to {location}")
        return asset

    @staticmethod
    def get_asset(db: Session, team_id: UUID, asset_id: UUID) -> Optional[Asset]:
        return db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.team_id == team_id,
        ).first()

    @staticmethod
    def list_assets(
        db: Session,
        team_id: UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Asset]:
        query = db.query(Asset).filter(Asset.team_id == team_id)
        if status:
            query = query.filter(Asset.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_asset_history(
        db: Session, team_id: UUID, asset_id: UUID, limit: int = 50
    ) -> list[AssetLocationEvent]:
        asset = db.query(Asset).filter(
            Asset.id == asset_id,
            Asset.team_id == team_id,
        ).first()
        
        if not asset:
            return []

        return db.query(AssetLocationEvent).filter(
            AssetLocationEvent.asset_id == asset_id
        ).order_by(AssetLocationEvent.created_at.desc()).limit(limit).all()