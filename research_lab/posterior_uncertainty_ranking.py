"""Posterior-aware ranking for observed real-market route transitions.

Research only. Combines posterior-updated success probability with a conservative
Beta posterior lower quantile approximation and capital growth. This keeps
aleatoric outcome estimates separate from epistemic sample uncertainty.
"""

from math import sqrt
from statistics import NormalDist

from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition

RANKING_VERSION = "0.1"


def posterior_parameters(
    transition: MarketRouteTransition,
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    prior_strength: float = 2.0,
) -> tuple[float, float]:
    if prior_strength <= 0:
        raise ValueError("prior_strength must be positive")
    p = max(0.0, min(1.0, float(transition.success_probability)))
    epsilon = 1e-6
    alpha = max(epsilon, p * prior_strength)
    beta = max(epsilon, (1.0 - p) * prior_strength)
    for outcome in outcomes:
        if outcome.opportunity_key == opportunity_key:
            if outcome.sold:
                alpha += 1.0
            else:
                beta += 1.0
    return alpha, beta


def posterior_lower_probability(
    transition: MarketRouteTransition,
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    credibility: float = 0.90,
    prior_strength: float = 2.0,
) -> float:
    if not 0.5 < credibility < 1.0:
        raise ValueError("credibility must be between 0.5 and 1")
    alpha, beta = posterior_parameters(transition, opportunity_key, outcomes, prior_strength)
    total = alpha + beta
    mean = alpha / total
    variance = (alpha * beta) / (total * total * (total + 1.0))
    z = NormalDist().inv_cdf(credibility)
    return max(0.0, mean - z * sqrt(variance))


def posterior_route_score(
    transition: MarketRouteTransition,
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    credibility: float = 0.90,
) -> float:
    lower = posterior_lower_probability(transition, opportunity_key, outcomes, credibility)
    growth = transition.success_capital / transition.required_capital
    return lower * growth
