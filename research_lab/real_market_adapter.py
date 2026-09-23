"""Adapter from Real Market observations to the existing Candidate Engine."""

from candidate_engine import create_candidate
from research_lab.real_market_schema import MarketObservation, validate_observation

ADAPTER_VERSION = "0.1"


def observation_to_candidate(observation: MarketObservation) -> dict:
    errors = validate_observation(observation)
    if errors:
        raise ValueError("; ".join(errors))

    metadata = {
        "real_market_schema_version": "0.1",
        "real_market_adapter_version": ADAPTER_VERSION,
        "external_id": observation.external_id,
        "source_url": observation.source_url,
        "currency": observation.currency,
        "gross_expected_sale_price": observation.expected_sale_price,
        "platform_fee": observation.platform_fee,
        "payment_fee": observation.payment_fee,
        "shipping_cost": observation.shipping_cost,
        "tax_cost": observation.tax_cost,
        "other_cost": observation.other_cost,
        "recovery_value": observation.recovery_value,
        "estimated_days_to_sale": observation.estimated_days_to_sale,
        "observed_at": observation.observed_at,
        "evidence_count": observation.evidence_count,
        "observation_confidence": observation.confidence,
    }

    return create_candidate(
        name=observation.name,
        purchase_price=observation.purchase_price,
        expected_sale_price=max(0.0, observation.net_sale_value),
        source=observation.source,
        category=observation.category,
        confidence=observation.sale_probability,
        metadata=metadata,
    )
