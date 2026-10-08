from __future__ import annotations

import logging
import re
from datetime import datetime
from io import BytesIO
from typing import Any, Optional
from uuid import UUID

import boto3
from PIL import Image
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.client import Client
from app.models.document import Document
from app.schemas.document import DocumentRead

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.s3_access_key_id,
    aws_secret_access_key=settings.s3_secret_access_key,
    region_name=settings.s3_region,
)


class DocumentService:
    @staticmethod
    def upload_document(
        db: Session,
        team_id: UUID,
        owner_id: UUID,
        filename: str,
        file_content: bytes,
        source_type: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> DocumentRead:
        try:
            s3_path = f"documents/{team_id}/{filename}"
            s3_client.put_object(
                Bucket=settings.s3_bucket_name,
                Key=s3_path,
                Body=file_content,
                Metadata={"team_id": str(team_id), "source_type": source_type},
            )

            document = Document(
                owner_id=owner_id,
                team_id=team_id,
                source_type=source_type,
                filename=filename,
                s3_path=s3_path,
                processing_status="uploaded",
                metadata=metadata or {},
            )
            db.add(document)
            db.commit()
            db.refresh(document)
            logger.info(f"Uploaded document {document.id} to S3")
            return DocumentRead.from_orm(document)
        except Exception as exc:
            logger.error(f"Failed to upload document: {exc}")
            raise

    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        try:
            image = Image.open(BytesIO(image_bytes))
            import pytesseract
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as exc:
            logger.error(f"OCR extraction failed: {exc}")
            return ""

    @staticmethod
    def normalize_text(raw_text: str) -> str:
        text = raw_text.replace("\n", " ").strip()
        cleaned = re.sub(r"\s+", " ", text)
        return cleaned

    @staticmethod
    def extract_client_from_text(db: Session, team_id: UUID, raw_text: str) -> Optional[UUID]:
        patterns = [
            r"(?i)(?:client|customer|bill to|billed to)[:\s]+([A-Za-z0-9 .&'-]+)",
            r"(?i)(?:from|from:)\s+([A-Za-z0-9 .&'-]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, raw_text)
            if matches:
                candidate = matches[0].strip()
                if len(candidate) > 2:
                    client = db.query(Client).filter(
                        Client.team_id == team_id,
                        Client.name.ilike(f"%{candidate}%"),
                    ).first()
                    if client:
                        return client.id

        return None

    @staticmethod
    def extract_monetary_amounts(raw_text: str) -> list[dict[str, Any]]:
        pattern = r"\$?([\d,]+\.?\d*)"
        matches = re.findall(pattern, raw_text)
        amounts = []
        for match in matches:
            try:
                amount = float(match.replace(",", ""))
                if 0 < amount < 1_000_000:
                    amounts.append({"amount": amount, "raw": match})
            except ValueError:
                continue
        return amounts

    @staticmethod
    def process_document(
        db: Session, document_id: UUID
    ) -> DocumentRead:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        try:
            document.processing_status = "processing"
            db.commit()

            s3_obj = s3_client.get_object(Bucket=settings.s3_bucket_name, Key=document.s3_path)
            file_content = s3_obj["Body"].read()

            if document.source_type in ["receipt", "invoice", "photo"]:
                raw_text = DocumentService.extract_text_from_image(file_content)
            else:
                raw_text = file_content.decode("utf-8", errors="ignore")

            document.raw_text = raw_text
            document.normalized_text = DocumentService.normalize_text(raw_text)
            document.confidence = 0.8

            client_id = DocumentService.extract_client_from_text(
                db, document.team_id, raw_text
            )
            amounts = DocumentService.extract_monetary_amounts(raw_text)

            document.extracted_data = {
                "client_id": str(client_id) if client_id else None,
                "amounts": amounts,
                "raw_text_length": len(raw_text),
            }

            document.processing_status = "completed"
            db.commit()
            db.refresh(document)
            logger.info(f"Processed document {document_id}")
            return DocumentRead.from_orm(document)
        except Exception as exc:
            document.processing_status = "failed"
            document.error_message = str(exc)
            db.commit()
            logger.error(f"Document processing failed {document_id}: {exc}")
            raise