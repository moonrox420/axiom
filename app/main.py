from __future__ import annotations

from decimal import Decimal
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import AxiomSettings
from .services import AxiomService

app = FastAPI(title="Axiom", version="0.1.0")
service = AxiomService(settings=AxiomSettings())


class IngestDocumentRequest(BaseModel):
    source_type: str = Field(..., description="One of: receipt, email, timesheet, pdf, voice, csv")
    raw_text: str = Field(..., min_length=1)
    metadata: dict[str, Any] | None = None


class GenerateInvoiceRequest(BaseModel):
    document_id: str = Field(..., description="Source document identifier")


class RegisterAssetRequest(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    confidence: Decimal = Decimal("0.8")
    status: str = "in_service"


class UpdateAssetLocationRequest(BaseModel):
    asset_id: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    confidence: Decimal = Decimal("0.8")
    evidence: str = ""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "Axiom"}


@app.post("/documents/ingest")
def ingest_document(payload: IngestDocumentRequest) -> dict[str, Any]:
    document = service.ingest_document(payload.source_type, payload.raw_text, payload.metadata or {})
    return {
        "id": document.id,
        "source_type": document.source_type,
        "normalized_text": document.normalized_text,
        "created_at": document.created_at.isoformat(),
    }


@app.post("/invoices/generate")
def generate_invoice(payload: GenerateInvoiceRequest) -> dict[str, Any]:
    if payload.document_id not in service.documents:
        raise HTTPException(status_code=404, detail="Document not found")
    invoice = service.build_invoice_from_document(payload.document_id)
    return {
        "id": invoice.id,
        "client_id": invoice.client_id,
        "invoice_number": invoice.invoice_number,
        "subtotal": str(invoice.subtotal),
        "tax": str(invoice.tax),
        "freight": str(invoice.freight),
        "total": str(invoice.total),
        "status": invoice.status,
        "evidence": invoice.evidence,
    }


@app.post("/assets/register")
def register_asset(payload: RegisterAssetRequest) -> dict[str, Any]:
    asset = service.register_asset(
        name=payload.name,
        category=payload.category,
        location=payload.location,
        source=payload.source,
        confidence=payload.confidence,
        status=payload.status,
    )
    return {
        "id": asset.id,
        "name": asset.name,
        "category": asset.category,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": str(asset.confidence),
        "last_seen_at": asset.last_seen_at.isoformat(),
    }


@app.post("/assets/location")
def update_asset_location(payload: UpdateAssetLocationRequest) -> dict[str, Any]:
    try:
        asset = service.update_asset_location(
            asset_id=payload.asset_id,
            location=payload.location,
            source=payload.source,
            confidence=payload.confidence,
            evidence=payload.evidence,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "id": asset.id,
        "name": asset.name,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": str(asset.confidence),
        "last_seen_at": asset.last_seen_at.isoformat(),
    }


@app.get("/exceptions")
def get_exception_queue() -> dict[str, Any]:
    return {"items": service.get_exception_queue()}


@app.get("/assets/{asset_id}")
def get_asset(asset_id: str) -> dict[str, Any]:
    asset = service.assets.get(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {
        "id": asset.id,
        "name": asset.name,
        "category": asset.category,
        "current_location": asset.current_location,
        "status": asset.status,
        "confidence": str(asset.confidence),
        "last_seen_at": asset.last_seen_at.isoformat(),
        "evidence": asset.evidence,
    }


@app.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str) -> dict[str, Any]:
    invoice = service.invoices.get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "client_id": invoice.client_id,
        "subtotal": str(invoice.subtotal),
        "tax": str(invoice.tax),
        "freight": str(invoice.freight),
        "total": str(invoice.total),
        "status": invoice.status,
        "line_items": [
            {
                "description": item.description,
                "quantity": str(item.quantity),
                "unit_cost": str(item.unit_cost),
                "tax_rate": str(item.tax_rate),
                "category": item.category,
                "freight": str(item.freight),
                "line_total": str(item.line_total),
            }
            for item in invoice.line_items
        ],
    }