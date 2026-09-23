"""Read-only source boundary for Real Market Engine research.

Connectors (Exa, marketplace APIs, files, etc.) should return raw dictionaries.
This module normalizes those records into MarketObservation without performing
purchases, listings, payments, or other external actions.
"""

from datetime import datetime, timezone
from typing import Any, Iterable

from research_lab.real_market_schema import MarketObservation, validate_observation

SOURCE_ADAPTER_VERSION = "0.1"

REQUIRED_RAW_FIELDS = (
    "external_id",
    "name",
    "category",
    "source",
    "currency",
    "purchase_price",
    "expected_sale_price",
    "sale_probability",
)


def _float(raw: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = raw.get(key, default)
    if value is None:
        return default
    return float(value)


def normalize_raw_observation(raw: dict[str, Any]) -> MarketObservation:
    missing = [key for key in REQUIRED_RAW_FIELDS if raw.get(key) in (None, "")]
    if missing:
        raise ValueError("missing required raw fields: " + ", ".join(missing))

    observed_at = raw.get("observed_at")
    if not observed_at:
        observed_at = datetime.now(timezone.utc).isoformat()

    metadata = dict(raw.get("metadata") or {})
    metadata["source_adapter_version"] = SOURCE_ADAPTER_VERSION

    observation = MarketObservation(
        external_id=str(raw["external_id"]),
        name=str(raw["name"]),
        category=str(raw["category"]),
        source=str(raw["source"]),
        source_url=raw.get("source_url"),
        currency=str(raw["currency"]).upper(),
        purchase_price=_float(raw, "purchase_price"),
        expected_sale_price=_float(raw, "expected_sale_price"),
        sale_probability=_float(raw, "sale_probability"),
        estimated_days_to_sale=(
            None if raw.get("estimated_days_to_sale") is None
            else _float(raw, "estimated_days_to_sale")
        ),
        platform_fee=_float(raw, "platform_fee"),
        payment_fee=_float(raw, "payment_fee"),
        shipping_cost=_float(raw, "shipping_cost"),
        tax_cost=_float(raw, "tax_cost"),
        other_cost=_float(raw, "other_cost"),
        recovery_value=(
            None if raw.get("recovery_value") is None
            else _float(raw, "recovery_value")
        ),
        observed_at=str(observed_at),
        evidence_count=int(raw.get("evidence_count", 0)),
        confidence=_float(raw, "confidence"),
        metadata=metadata,
    )

    errors = validate_observation(observation)
    if errors:
        raise ValueError("; ".join(errors))

    return observation


def normalize_source_batch(records: Iterable[dict[str, Any]]) -> tuple[list[MarketObservation], list[dict[str, Any]]]:
    accepted = []
    rejected = []

    for index, raw in enumerate(records):
        try:
            accepted.append(normalize_raw_observation(raw))
        except (TypeError, ValueError) as exc:
            rejected.append(
                {
                    "index": index,
                    "external_id": raw.get("external_id") if isinstance(raw, dict) else None,
                    "reason": str(exc),
                }
            )

    return accepted, rejected
