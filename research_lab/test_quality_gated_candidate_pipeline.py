"""Offline checks for quality-gated Candidate Pipeline integration."""

from research_lab.market_evidence_estimator import MarketEstimate
from research_lab.quality_gated_candidate_pipeline import evaluate_quality_gated_estimates


def estimate(name, confidence, evidence, sources):
    return MarketEstimate(
        name=name, category="test", currency="JPY", purchase_price=100,
        expected_sale_price=160, sale_probability=.8, estimated_days_to_sale=2,
        recovery_value=50, confidence=confidence, evidence_count=evidence,
        source_count=sources,
    )


def main():
    rows = [
        estimate("strong", .8, 8, 3),
        estimate("weak", .2, 1, 1),
    ]
    result = evaluate_quality_gated_estimates(rows, 100)
    assert result["input_estimates"] == 1
    assert result["quality_accepted"] == 1
    assert result["quality_rejected"] == 1
    assert result["quality_rejections"][0]["name"] == "weak"
    assert result["quality_rejection_reasons"]["low_confidence"] == 1
    print("quality-gated candidate pipeline tests passed")


if __name__ == "__main__":
    main()
