from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentBase(BaseModel):
    source_type: str
    filename: str


class DocumentRead(DocumentBase):
    id: UUID
    owner_id: UUID
    team_id: UUID
    s3_path: str | None = None
    confidence: float
    processing_status: str
    extracted_data: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True