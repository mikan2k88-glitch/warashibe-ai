"""Adapter from Real Market observations to the existing Candidate Engine."""

from candidate_engine import create_candidate
from research_lab.real_market_schema import MarketObservation, validate_observation

ADAPTER_VERSION = "0.2"


def observation_to_candidate(observation: MarketObservation) -> dict:
    errors = validate_observation(observation)
    if errors:
        raise ValueError("; ".join(errors))

    source_metadata = dict(observation.metadata or {})
    metadata = {
        **source_metadata,
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
        confidence=observation.confidence,
        success_probability=observation.sale_probability,
        metadata=metadata,
        estimated_days_to_sell=observation.estimated_days_to_sale,
        estimated_fees=(
            observation.platform_fee
            + observation.payment_fee
            + observation.tax_cost
            + observation.other_cost
        ),
        package_size_class=source_metadata.get("package_size_class"),
        weight_grams=source_metadata.get("weight_grams"),
        shipping_cost_jpy=source_metadata.get("shipping_cost_jpy"),
        fragility_score=source_metadata.get("fragility_score"),
        storage_score=source_metadata.get("storage_score"),
        domestic_shipping=source_metadata.get("domestic_shipping"),
    )
