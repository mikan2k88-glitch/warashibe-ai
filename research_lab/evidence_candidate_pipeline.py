"""Research pipeline from aggregated market evidence to existing Candidate Pipeline.

Read-only research integration. Production market discovery and Route Engine
remain unchanged.
"""

from candidate_engine import create_candidate
from candidate_pipeline import evaluate_candidates
from research_lab.market_evidence_estimator import MarketEstimate

PIPELINE_VERSION = "0.1"


def estimate_to_candidate(estimate: MarketEstimate) -> dict:
    metadata = {
        "real_market_pipeline_version": PIPELINE_VERSION,
        "currency": estimate.currency,
        "estimated_days_to_sale": estimate.estimated_days_to_sale,
        "recovery_value": estimate.recovery_value,
        "evidence_count": estimate.evidence_count,
        "source_count": estimate.source_count,
        "evidence_confidence": estimate.confidence,
        "gross_expected_sale_price": estimate.expected_sale_price,
    }

    # Existing Candidate Engine uses confidence as the modeled success
    # probability. Evidence confidence remains separate metadata so data
    # quality is not confused with sale probability.
    return create_candidate(
        name=estimate.name,
        purchase_price=estimate.purchase_price,
        expected_sale_price=estimate.expected_sale_price,
        source="real_market_evidence",
        category=estimate.category,
        confidence=estimate.sale_probability,
        metadata=metadata,
    )


def evaluate_market_estimates(estimates: list[MarketEstimate], current_capital: float) -> dict:
    candidates = [estimate_to_candidate(estimate) for estimate in estimates]
    result = evaluate_candidates(candidates, current_capital)
    result["real_market_pipeline_version"] = PIPELINE_VERSION
    result["input_estimates"] = len(estimates)
    return result
