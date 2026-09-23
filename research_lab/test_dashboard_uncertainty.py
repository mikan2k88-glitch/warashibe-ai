"""Tests for dashboard uncertainty monitor."""

from research_lab.dashboard_uncertainty import demo_uncertainty_metrics


def run():
    m = demo_uncertainty_metrics()
    assert m["raw_outcome_count"] == 12
    assert m["evidence_count"] == 12
    assert m["source_count"] == 3
    assert 0 <= m["conservative_probability_percent"] <= m["posterior_probability_percent"] <= 100
    assert m["posterior_std_percent"] > 0


if __name__ == "__main__":
    run()
    print("DASHBOARD UNCERTAINTY: PASSED")
