"""Evidence aggregation for Real Market Engine research.

Combines multiple read-only observations of the same market opportunity into a
conservative estimate. No external actions are performed.
"""

from dataclasses import dataclass
from statistics import median

from research_lab.real_market_schema import MarketObservation, validate_observation

ESTIMATOR_VERSION = "0.1"


@dataclass(frozen=True)
class MarketEstimate:
    name: str
    category: str
    currency: str
    purchase_price: float
    expected_sale_price: float
    sale_probability: float
    estimated_days_to_sale: float | None
    recovery_value: float | None
    confidence: float
    evidence_count: int
    source_count: int


def _bounded(value):
    return max(0.0, min(1.0, float(value)))


def _median_optional(values):
    clean = [float(v) for v in values if v is not None]
    return median(clean) if clean else None


def estimate_market(observations: list[MarketObservation]) -> MarketEstimate:
    if not observations:
        raise ValueError("at least one observation is required")

    for observation in observations:
        errors = validate_observation(observation)
        if errors:
            raise ValueError("; ".join(errors))

    currencies = {x.currency for x in observations}
    categories = {x.category for x in observations}
    if len(currencies) != 1:
        raise ValueError("mixed currencies are not supported")
    if len(categories) != 1:
        raise ValueError("mixed categories are not supported")

    purchase_price = median(x.purchase_price for x in observations)
    expected_sale_price = median(x.expected_sale_price for x in observations)
    sale_probability = median(x.sale_probability for x in observations)
    days = _median_optional(x.estimated_days_to_sale for x in observations)
    recovery = _median_optional(x.recovery_value for x in observations)

    source_count = len({x.source for x in observations})
    evidence_count = sum(max(1, x.evidence_count) for x in observations)

    # Confidence deliberately rewards independent sources and sample depth,
    # while remaining capped and discounted by the observations' own quality.
    source_factor = min(1.0, source_count / 3.0)
    evidence_factor = min(1.0, evidence_count / 12.0)
    quality_factor = median(x.confidence for x in observations)
    confidence = _bounded(
        0.40 * quality_factor
        + 0.35 * source_factor
        + 0.25 * evidence_factor
    )

    return MarketEstimate(
        name=observations[0].name,
        category=observations[0].category,
        currency=observations[0].currency,
        purchase_price=float(purchase_price),
        expected_sale_price=float(expected_sale_price),
        sale_probability=float(sale_probability),
        estimated_days_to_sale=None if days is None else float(days),
        recovery_value=None if recovery is None else float(recovery),
        confidence=confidence,
        evidence_count=evidence_count,
        source_count=source_count,
    )
