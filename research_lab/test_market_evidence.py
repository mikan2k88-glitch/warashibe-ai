"""Tests for market evidence aggregation."""

from research_lab.market_evidence_estimator import estimate_market
from research_lab.real_market_schema import MarketObservation


def obs(source, buy, sell, p, days, recovery, evidence, confidence):
    return MarketObservation(
        external_id=f"{source}-{buy}",
        name="中古カメラ",
        category="camera",
        source=source,
        source_url=None,
        currency="JPY",
        purchase_price=buy,
        expected_sale_price=sell,
        sale_probability=p,
        estimated_days_to_sale=days,
        recovery_value=recovery,
        evidence_count=evidence,
        confidence=confidence,
    )


def run():
    estimate = estimate_market(
        [
            obs("source-a", 10000, 16000, 0.60, 8, 7000, 4, 0.70),
            obs("source-b", 11000, 15000, 0.70, 6, 7500, 5, 0.80),
            obs("source-c", 9000, 17000, 0.65, 7, 6500, 3, 0.75),
        ]
    )

    assert estimate.purchase_price == 10000
    assert estimate.expected_sale_price == 16000
    assert estimate.sale_probability == 0.65
    assert estimate.estimated_days_to_sale == 7
    assert estimate.recovery_value == 7000
    assert estimate.source_count == 3
    assert estimate.evidence_count == 12
    assert abs(estimate.confidence - 0.90) < 1e-12

    single = estimate_market([obs("one", 100, 150, 0.8, None, None, 1, 0.5)])
    assert single.source_count == 1
    assert single.confidence < estimate.confidence

    try:
        estimate_market([])
        raise AssertionError("empty observations should fail")
    except ValueError:
        pass


if __name__ == "__main__":
    run()
    print("MARKET EVIDENCE ESTIMATOR: PASSED")
