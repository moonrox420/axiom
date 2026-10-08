from __future__ import annotations

import re
from datetime import timedelta
from decimal import Decimal
from typing import Any

from .config import AxiomSettings
from .models import (
    Asset,
    AssetLocationEvent,
    Client,
    ExceptionItem,
    InvoiceDraft,
    LineItem,
    SourceDocument,
    to_decimal,
    utc_now,
)


class AxiomService:
    def __init__(self, settings: AxiomSettings | None = None) -> None:
        self.settings = settings or AxiomSettings()
        self.clients: dict[str, Client] = {}
        self.documents: dict[str, SourceDocument] = {}
        self.invoices: dict[str, InvoiceDraft] = {}
        self.assets: dict[str, Asset] = {}
        self.asset_history: dict[str, list[AssetLocationEvent]] = {}
        self.exceptions: dict[str, ExceptionItem] = {}
        self._client_name_index: dict[str, str] = {}

    def normalize_name(self, value: str) -> str:
        if not value:
            return ""
        cleaned = re.sub(r"\s+", " ", value.strip())
        return cleaned.title()

    def normalize_email(self, value: str | None) -> str | None:
        if not value:
            return None
        return value.strip().lower()

    def create_or_update_client(
        self,
        name: str,
        email: str | None = None,
        address: str | None = None,
        tax_id: str | None = None,
    ) -> Client:
        safe_name = self.normalize_name(name)
        existing_id = self._client_name_index.get(safe_name)
        if existing_id:
            client = self.clients[existing_id]
            if email:
                client.email = self.normalize_email(email)
            if address:
                client.address = address.strip()
            if tax_id:
                client.tax_id = tax_id.strip()
            return client

        client_id = f"client_{len(self.clients) + 1:04d}"
        client = Client(
            id=client_id,
            name=safe_name,
            email=self.normalize_email(email),
            address=address.strip() if address else None,
            tax_id=tax_id.strip() if tax_id else None,
        )
        self.clients[client_id] = client
        self._client_name_index[safe_name] = client_id
        return client

    def ingest_document(
        self, source_type: str, raw_text: str, metadata: dict[str, Any] | None = None
    ) -> SourceDocument:
        metadata = metadata or {}
        document = SourceDocument(
            id=f"doc_{len(self.documents) + 1:04d}",
            source_type=source_type,
            raw_text=raw_text,
            normalized_text=self._normalize_document_text(raw_text),
            metadata=metadata,
        )
        self.documents[document.id] = document
        return document

    def _normalize_document_text(self, raw_text: str) -> str:
        text = raw_text.replace(r"\n", "\n").strip()
        cleaned = re.sub(r"\s+", " ", text)
        return cleaned

    def extract_client_from_text(self, raw_text: str) -> Client | None:
        matches = re.findall(
            r"(?i)(?:client|customer|bill to|billed to)[:\s]+([A-Za-z0-9 .&'-]+)",
            raw_text,
        )
        if matches:
            candidate = matches[0].strip()
            if candidate:
                return self.create_or_update_client(candidate)
        return None

    def parse_line_items_from_text(self, raw_text: str) -> list[LineItem]:
        items: list[LineItem] = []
        pattern = re.compile(
            r"(?P<desc>[A-Za-z0-9 /&.-]+?)\s+(?P<qty>\d+(?:\.\d+)?)\s*[@xX]\s*(?P<unit>\d+(?:\.\d+)?)",
            re.IGNORECASE,
        )
        matches = pattern.findall(raw_text)
        for desc, qty, unit in matches:
            items.append(
                LineItem(
                    description=desc.strip(),
                    quantity=to_decimal(qty),
                    unit_cost=to_decimal(unit),
                    tax_rate=Decimal(str(self.settings.tax_rate)),
                    category="service",
                    freight=Decimal(0),
                )
            )
        if not items:
            match = re.search(r"\$?(\d+(?:\.\d+)?)", raw_text)
            unit_cost = to_decimal(match.group(1)) if match else Decimal(0)
            items.append(
                LineItem(
                    description="General service",
                    quantity=Decimal(1),
                    unit_cost=unit_cost,
                    tax_rate=Decimal(str(self.settings.tax_rate)),
                    category="service",
                    freight=Decimal(0),
                )
            )
        return items

    def build_invoice_from_document(self, document_id: str) -> InvoiceDraft:
        document = self.documents[document_id]
        client = self.extract_client_from_text(
            document.normalized_text
        ) or self.create_or_update_client("Unassigned Client")
        items = self.parse_line_items_from_text(document.normalized_text)

        invoice = InvoiceDraft(
            id=f"inv_{len(self.invoices) + 1:04d}",
            client_id=client.id,
            invoice_number=f"AX-{utc_now().strftime('%Y%m%d')}-{len(self.invoices) + 1:04d}",
            issue_date=utc_now(),
            due_date=utc_now() + timedelta(days=14),
            status="draft",
            currency=self.settings.default_currency,
            line_items=items,
            notes=f"Generated from {document.source_type} document.",
            evidence=[document.id],
        )
        invoice.apply_totals()
        self.invoices[invoice.id] = invoice
        return invoice

    def register_asset(
        self,
        name: str,
        category: str,
        location: str,
        source: str,
        confidence: Decimal = Decimal("0.8"),
        status: str = "in_service",
    ) -> Asset:
        asset_id = f"asset_{len(self.assets) + 1:04d}"
        asset = Asset(
            id=asset_id,
            name=self.normalize_name(name),
            category=category.strip(),
            current_location=location.strip(),
            last_seen_at=utc_now(),
            status=status,
            confidence=confidence,
            evidence=[f"{source}:{location}"],
        )
        self.assets[asset_id] = asset
        self.asset_history.setdefault(asset_id, []).append(
            AssetLocationEvent(
                asset_id=asset_id,
                location=location.strip(),
                observed_at=asset.last_seen_at,
                source=source,
                confidence=confidence,
                evidence=f"{source}:{location}",
            )
        )
        return asset

    def update_asset_location(
        self,
        asset_id: str,
        location: str,
        source: str,
        confidence: Decimal = Decimal("0.8"),
        evidence: str = "",
    ) -> Asset:
        asset = self.assets.get(asset_id)
        if not asset:
            raise KeyError(f"Asset {asset_id} not found")

        asset.current_location = location.strip()
        asset.last_seen_at = utc_now()
        asset.confidence = confidence
        asset.evidence.append(f"{source}:{location}" if not evidence else evidence)
        self.asset_history.setdefault(asset_id, []).append(
            AssetLocationEvent(
                asset_id=asset_id,
                location=location.strip(),
                observed_at=asset.last_seen_at,
                source=source,
                confidence=confidence,
                evidence=evidence or f"{source}:{location}",
            )
        )
        return asset

    def check_for_exceptions(self) -> list[ExceptionItem]:
        exceptions: list[ExceptionItem] = []
        for invoice in self.invoices.values():
            if invoice.status == "exception":
                continue
            if not invoice.client_id:
                exceptions.append(
                    ExceptionItem(
                        id=f"exc_{len(self.exceptions)+1:04d}",
                        entity_type="invoice",
                        entity_id=invoice.id,
                        reason="Invoice is missing a valid client record.",
                        severity="high",
                        evidence=invoice.evidence,
                    )
                )
        for asset in self.assets.values():
            if asset.confidence < Decimal("0.6"):
                exceptions.append(
                    ExceptionItem(
                        id=f"exc_{len(self.exceptions)+1:04d}",
                        entity_type="asset",
                        entity_id=asset.id,
                        reason="Location confidence is below acceptable threshold.",
                        severity="medium",
                        evidence=asset.evidence,
                    )
                )
        for exc in exceptions:
            self.exceptions[exc.id] = exc
        return exceptions

    def get_exception_queue(self) -> list[dict[str, Any]]:
        items = list(self.exceptions.values())
        return [
            {
                "id": item.id,
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "reason": item.reason,
                "severity": item.severity,
                "evidence": item.evidence,
                "created_at": item.created_at.isoformat(),
                "resolved": item.resolved,
            }
            for item in items
        ]