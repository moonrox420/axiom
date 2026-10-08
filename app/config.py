from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AxiomSettings:
    app_name: str = "Axiom"
    default_currency: str = "USD"
    tax_rate: float = 0.0825
    freight_default: float = 0.0
    max_exception_items: int = 50

    def as_dict(self) -> dict[str, Any]:
        return {
            "app_name": self.app_name,
            "default_currency": self.default_currency,
            "tax_rate": self.tax_rate,
            "freight_default": self.freight_default,
            "max_exception_items": self.max_exception_items,
        }