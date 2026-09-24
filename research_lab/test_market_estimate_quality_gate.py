"""Offline checks for market estimate quality gating."""

from research_lab.market_estimate_quality_gate import evaluate_market_estimate
from research_lab.market_evidence_estimator import MarketEstimate


def estimate(confidence=.7, evidence=6, sources=3):
    return MarketEstimate(
        name="Product", category="test", currency="JPY", purchase_price=100,
        expected_sale_price=150, sale_probability=.7, estimated_days_to_sale=3,
        recovery_value=50, confidence=confidence, evidence_count=evidence,
        source_count=sources,
    )


def main():
    assert evaluate_market_estimate(estimate()).accepted

    weak = evaluate_market_estimate(estimate(confidence=.2, evidence=1, sources=1))
    assert not weak.accepted
    assert weak.reasons == (
        "low_confidence", "insufficient_evidence", "insufficient_source_diversity"
    )

    one_source = evaluate_market_estimate(estimate(sources=1))
    assert not one_source.accepted
    assert one_source.reasons == ("insufficient_source_diversity",)
    print("market estimate quality gate tests passed")


if __name__ == "__main__":
    main()
