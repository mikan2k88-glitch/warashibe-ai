"""Tests for raw sale-outcome calibration."""

from research_lab.raw_outcome_calibration import SaleOutcome, calibrate_outcomes


def run():
    outcomes = [
        SaleOutcome("camera-a", True, 4),
        SaleOutcome("camera-a", True, 8),
        SaleOutcome("camera-a", False, 14),
        SaleOutcome("camera-b", False, 5),
    ]

    result = calibrate_outcomes("camera-a", outcomes)
    assert result.successes == 2
    assert result.failures == 1
    assert result.observations == 3
    assert result.posterior_alpha == 3.0
    assert result.posterior_beta == 2.0
    assert result.posterior_mean == 0.6
    assert round(result.empirical_sale_rate, 6) == round(2 / 3, 6)
    assert result.mean_days_to_outcome == 26 / 3

    empty = calibrate_outcomes("missing", outcomes)
    assert empty.observations == 0
    assert empty.posterior_mean == 0.5
    assert empty.empirical_sale_rate is None

    try:
        calibrate_outcomes("camera-a", outcomes, prior_alpha=0)
        raise AssertionError("invalid prior accepted")
    except ValueError:
        pass


if __name__ == "__main__":
    run()
    print("RAW OUTCOME CALIBRATION: PASSED")
