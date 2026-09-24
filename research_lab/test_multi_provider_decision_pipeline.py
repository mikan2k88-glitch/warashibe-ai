"""Checks for multi-provider snapshot to decision integration."""

from research_lab.multi_provider_decision_pipeline import run_multi_provider_decision
from research_lab.test_multi_provider_market_snapshot import Provider


def main():
    result = run_multi_provider_decision(
        [Provider("market-a", 10000), Provider("market-b", 10500)],
        "camera", 11000,
        min_confidence=.5, min_evidence_count=3, min_source_count=2,
    )
    assert result["snapshot_provider_count"] == 2
    assert result["snapshot_raw_count"] == 2
    assert result["quality_accepted"] == 1
    assert result["quality_rejected"] == 0
    assert result["input_estimates"] == 1
    print("multi-provider decision pipeline tests passed")


if __name__ == "__main__":
    main()
