from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ExceptionRead(BaseModel):
    id: UUID
    team_id: UUID
    entity_type: str
    entity_id: UUID
    reason: str
    severity: str
    status: str
    evidence: list[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True