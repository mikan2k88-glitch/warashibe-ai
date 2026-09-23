"""Posterior sale-outcome integration for observed real-market routes.

Research only. Raw Bernoulli outcomes can update an observed transition's sale
probability through the Beta posterior produced by raw_outcome_calibration.
When no matching raw outcomes exist, the original market estimate is preserved.
The production Route Engine is unchanged.
"""

from dataclasses import replace

from research_lab.raw_outcome_calibration import SaleOutcome, calibrate_outcomes
from research_lab.real_market_route_bridge import MarketRouteTransition

INTEGRATION_VERSION = "0.1"


def posterior_transition(
    transition: MarketRouteTransition,
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    prior_strength: float = 2.0,
) -> MarketRouteTransition:
    """Return a transition updated by matching raw outcomes.

    The market estimate supplies the prior mean. ``prior_strength`` controls
    how many pseudo-observations that estimate contributes. This avoids
    replacing a useful market estimate with a fixed 0.5 prior before any raw
    outcomes exist.
    """
    if prior_strength <= 0:
        raise ValueError("prior_strength must be positive")

    matching = [x for x in outcomes if x.opportunity_key == opportunity_key]
    if not matching:
        return transition

    p = max(0.0, min(1.0, float(transition.success_probability)))
    # Keep Beta parameters strictly positive at probability boundaries.
    epsilon = 1e-6
    prior_alpha = max(epsilon, p * prior_strength)
    prior_beta = max(epsilon, (1.0 - p) * prior_strength)
    calibration = calibrate_outcomes(
        opportunity_key,
        matching,
        prior_alpha=prior_alpha,
        prior_beta=prior_beta,
    )
    return replace(transition, success_probability=calibration.posterior_mean)
