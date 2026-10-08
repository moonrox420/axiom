from __future__ import annotations

from sqlalchemy import Column, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from .base import Base, IDMixin, TimestampMixin


class Document(Base, IDMixin, TimestampMixin):
    __tablename__ = "documents"
    
    owner_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    team_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)
    filename = Column(String(255), nullable=False)
    s3_path = Column(String(1000), nullable=True)
    raw_text = Column(Text, nullable=True)
    normalized_text = Column(Text, nullable=True)
    extracted_data = Column(JSONB, default={}, nullable=False)
    confidence = Column(Float, default=0.0)
    metadata = Column(JSONB, default={}, nullable=False)
    processing_status = Column(String(50), default="pending")
    error_message = Column(Text, nullable=True)
    
    owner = relationship("User", back_populates="documents")
    invoices = relationship("Invoice", secondary="invoice_documents", back_populates="documents")