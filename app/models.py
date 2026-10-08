from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Literal


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_decimal(value: str | float | Decimal | None, places: int = 2) -> Decimal:
    if value is None:
        return Decimal(0).quantize(Decimal("0.01"))
    quant = Decimal(1).scaleb(-places)
    return Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)


def format_money(value: str | float | Decimal) -> str:
    return f"${to_decimal(value):,.2f}"


@dataclass
class Client:
    id: str
    name: str
    email: str | None = None
    address: str | None = None
    tax_id: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class LineItem:
    description: str
    quantity: Decimal = Decimal(1)
    unit_cost: Decimal = Decimal(0)
    tax_rate: Decimal = Decimal(0)
    category: str = "service"
    freight: Decimal = Decimal(0)
    notes: str = ""

    @property
    def line_total(self) -> Decimal:
        base = self.quantity * self.unit_cost
        taxes = base * self.tax_rate
        return base + taxes + self.freight


@dataclass
class InvoiceDraft:
    id: str
    client_id: str
    invoice_number: str
    issue_date: datetime
    due_date: datetime
    status: Literal["draft", "ready", "sent", "paid", "exception"] = "draft"
    currency: str = "USD"
    subtotal: Decimal = Decimal(0)
    tax: Decimal = Decimal(0)
    freight: Decimal = Decimal(0)
    total: Decimal = Decimal(0)
    line_items: list[LineItem] = field(default_factory=list)
    notes: str = ""
    evidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)

    def apply_totals(self) -> None:
        self.subtotal = sum(
            (item.quantity * item.unit_cost) for item in self.line_items
        )
        self.tax = sum(
            (item.quantity * item.unit_cost * item.tax_rate) for item in self.line_items
        )
        self.freight = sum((item.freight for item in self.line_items), Decimal(0))
        self.total = self.subtotal + self.tax + self.freight


@dataclass
class Asset:
    id: str
    name: str
    category: str
    current_location: str
    last_seen_at: datetime
    status: Literal["in_service", "staged", "maintenance", "lost", "missing"] = (
        "in_service"
    )
    confidence: Decimal = Decimal("0.8")
    evidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class AssetLocationEvent:
    asset_id: str
    location: str
    observed_at: datetime
    source: str
    confidence: Decimal
    evidence: str


@dataclass
class SourceDocument:
    id: str
    source_type: str
    raw_text: str
    normalized_text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=utc_now)


@dataclass
class ExceptionItem:
    id: str
    entity_type: str
    entity_id: str
    reason: str
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    evidence: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=utc_now)
    resolved: bool = False
