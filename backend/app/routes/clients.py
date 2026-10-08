from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.client import ClientCreate, ClientRead, ClientUpdate
from app.services.client_service import ClientService

router = APIRouter()


@router.post("", response_model=ClientRead)
def create_client(
    team_id: UUID,
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    return ClientService.create_client(db, team_id, payload)


@router.get("/{client_id}", response_model=ClientRead)
def get_client(
    team_id: UUID,
    client_id: UUID,
    db: Session = Depends(get_db),
):
    client = ClientService.get_client(db, team_id, client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@router.get("", response_model=list[ClientRead])
def list_clients(
    team_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return ClientService.list_clients(db, team_id, skip, limit)


@router.put("/{client_id}", response_model=ClientRead)
def update_client(
    team_id: UUID,
    client_id: UUID,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
):
    client = ClientService.update_client(db, team_id, client_id, payload)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return client


@router.delete("/{client_id}")
def delete_client(
    team_id: UUID,
    client_id: UUID,
    db: Session = Depends(get_db),
):
    success = ClientService.delete_client(db, team_id, client_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )
    return {"status": "deleted"}