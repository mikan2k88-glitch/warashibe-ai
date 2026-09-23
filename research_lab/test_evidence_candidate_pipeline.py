"""Integration test: market evidence -> Candidate Pipeline."""

from research_lab.evidence_candidate_pipeline import (
    estimate_to_candidate,
    evaluate_market_estimates,
)
from research_lab.market_evidence_estimator import MarketEstimate


def estimate(name, buy, sell, probability, confidence):
    return MarketEstimate(
        name=name,
        category="camera",
        currency="JPY",
        purchase_price=buy,
        expected_sale_price=sell,
        sale_probability=probability,
        estimated_days_to_sale=7,
        recovery_value=buy * 0.6,
        confidence=confidence,
        evidence_count=12,
        source_count=3,
    )


def run():
    strong = estimate("Evidence Camera A", 10000, 18000, 0.75, 0.90)
    weak = estimate("Evidence Camera B", 10000, 12000, 0.20, 0.30)
    expensive = estimate("Evidence Camera C", 20000, 40000, 0.80, 0.90)

    candidate = estimate_to_candidate(strong)
    assert candidate["source"] == "real_market_evidence"
    assert candidate["confidence"] == 0.75
    assert candidate["metadata"]["evidence_confidence"] == 0.90

    result = evaluate_market_estimates([strong, weak, expensive], 10000)
    assert result["real_market_pipeline_version"] == "0.1"
    assert result["input_estimates"] == 3
    assert result["total_candidates"] == 3
    assert result["best_candidate"] is not None
    assert result["best_candidate"]["name"] == "Evidence Camera A"

    blocked_names = {x["name"] for x in result["danger_blocked"]}
    capital_blocked_names = {x["candidate"]["name"] for x in result["capital_blocked"]}
    assert "Evidence Camera B" in blocked_names
    assert "Evidence Camera C" in capital_blocked_names


if __name__ == "__main__":
    run()
    print("EVIDENCE TO CANDIDATE PIPELINE: PASSED")
