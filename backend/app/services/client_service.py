from __future__ import annotations

import logging
import re
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate

logger = logging.getLogger(__name__)


class ClientService:
    @staticmethod
    def normalize_name(value: str) -> str:
        if not value:
            return ""
        cleaned = re.sub(r"\s+", " ", value.strip())
        return cleaned.title()

    @staticmethod
    def normalize_email(value: str | None) -> str | None:
        if not value:
            return None
        return value.strip().lower()

    @staticmethod
    def create_client(
        db: Session, team_id: UUID, payload: ClientCreate
    ) -> ClientRead:
        existing = db.query(Client).filter(
            Client.team_id == team_id,
            Client.name == ClientService.normalize_name(payload.name),
        ).first()
        
        if existing:
            logger.warning(f"Client already exists: {existing.id}")
            return ClientRead.from_orm(existing)

        client = Client(
            team_id=team_id,
            name=ClientService.normalize_name(payload.name),
            email=ClientService.normalize_email(payload.email),
            phone=payload.phone,
            address=payload.address,
            tax_id=payload.tax_id,
            payment_terms_days=payload.payment_terms_days,
            notes=payload.notes,
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        logger.info(f"Created client {client.id} for team {team_id}")
        return ClientRead.from_orm(client)

    @staticmethod
    def get_client(db: Session, team_id: UUID, client_id: UUID) -> ClientRead | None:
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.team_id == team_id,
        ).first()
        return ClientRead.from_orm(client) if client else None

    @staticmethod
    def list_clients(db: Session, team_id: UUID, skip: int = 0, limit: int = 100) -> list[ClientRead]:
        clients = db.query(Client).filter(
            Client.team_id == team_id
        ).offset(skip).limit(limit).all()
        return [ClientRead.from_orm(c) for c in clients]

    @staticmethod
    def update_client(
        db: Session, team_id: UUID, client_id: UUID, payload: ClientUpdate
    ) -> ClientRead | None:
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.team_id == team_id,
        ).first()
        
        if not client:
            return None

        if payload.name is not None:
            client.name = ClientService.normalize_name(payload.name)
        if payload.email is not None:
            client.email = ClientService.normalize_email(payload.email)
        if payload.phone is not None:
            client.phone = payload.phone
        if payload.address is not None:
            client.address = payload.address
        if payload.tax_id is not None:
            client.tax_id = payload.tax_id
        if payload.payment_terms_days is not None:
            client.payment_terms_days = payload.payment_terms_days
        if payload.notes is not None:
            client.notes = payload.notes

        db.commit()
        db.refresh(client)
        logger.info(f"Updated client {client_id}")
        return ClientRead.from_orm(client)

    @staticmethod
    def delete_client(db: Session, team_id: UUID, client_id: UUID) -> bool:
        client = db.query(Client).filter(
            Client.id == client_id,
            Client.team_id == team_id,
        ).first()
        
        if not client:
            return False

        db.delete(client)
        db.commit()
        logger.info(f"Deleted client {client_id}")
        return True