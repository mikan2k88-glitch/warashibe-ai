"""Canonical observation schema for the future Real Market Engine.

Research-only boundary layer. External market connectors should first produce
MarketObservation objects; adapters can then convert validated observations to
the existing Candidate Engine format.

No external API, marketplace, payment system, or production route is changed.
"""

from dataclasses import asdict, dataclass, field
from typing import Any

SCHEMA_VERSION = "0.1"


@dataclass(frozen=True)
class MarketObservation:
    external_id: str
    name: str
    category: str
    source: str
    source_url: str | None
    currency: str
    purchase_price: float
    expected_sale_price: float
    sale_probability: float
    estimated_days_to_sale: float | None = None
    platform_fee: float = 0.0
    payment_fee: float = 0.0
    shipping_cost: float = 0.0
    tax_cost: float = 0.0
    other_cost: float = 0.0
    recovery_value: float | None = None
    observed_at: str | None = None
    evidence_count: int = 0
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_cost(self) -> float:
        return (
            self.purchase_price
            + self.platform_fee
            + self.payment_fee
            + self.shipping_cost
            + self.tax_cost
            + self.other_cost
        )

    @property
    def net_sale_value(self) -> float:
        return self.expected_sale_price - (
            self.platform_fee
            + self.payment_fee
            + self.shipping_cost
            + self.tax_cost
            + self.other_cost
        )

    @property
    def expected_net_profit(self) -> float:
        return self.sale_probability * self.net_sale_value - self.purchase_price

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        data["total_cost"] = self.total_cost
        data["net_sale_value"] = self.net_sale_value
        data["expected_net_profit"] = self.expected_net_profit
        return data


def validate_observation(observation: MarketObservation) -> list[str]:
    errors = []

    for field_name in ("external_id", "name", "category", "source", "currency"):
        if not str(getattr(observation, field_name, "")).strip():
            errors.append(f"{field_name} is required")

    if observation.purchase_price < 0:
        errors.append("purchase_price must be >= 0")
    if observation.expected_sale_price < 0:
        errors.append("expected_sale_price must be >= 0")
    if not 0.0 <= observation.sale_probability <= 1.0:
        errors.append("sale_probability must be between 0 and 1")
    if not 0.0 <= observation.confidence <= 1.0:
        errors.append("confidence must be between 0 and 1")
    if observation.estimated_days_to_sale is not None and observation.estimated_days_to_sale < 0:
        errors.append("estimated_days_to_sale must be >= 0")
    if observation.recovery_value is not None and observation.recovery_value < 0:
        errors.append("recovery_value must be >= 0")

    for field_name in (
        "platform_fee", "payment_fee", "shipping_cost", "tax_cost", "other_cost"
    ):
        if getattr(observation, field_name) < 0:
            errors.append(f"{field_name} must be >= 0")

    if observation.evidence_count < 0:
        errors.append("evidence_count must be >= 0")

    return errors
