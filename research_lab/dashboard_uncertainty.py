"""Dashboard-facing uncertainty metrics for posterior route research."""

from math import sqrt

from research_lab.posterior_uncertainty_ranking import (
    posterior_lower_probability,
    posterior_parameters,
)
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import MarketRouteTransition

MONITOR_VERSION = "0.1"


def uncertainty_metrics(
    transition: MarketRouteTransition,
    opportunity_key: str,
    outcomes: list[SaleOutcome],
    credibility: float = 0.90,
) -> dict:
    alpha, beta = posterior_parameters(transition, opportunity_key, outcomes)
    total = alpha + beta
    mean = alpha / total
    std = sqrt((alpha * beta) / (total * total * (total + 1.0)))
    lower = posterior_lower_probability(transition, opportunity_key, outcomes, credibility)
    matching = [x for x in outcomes if x.opportunity_key == opportunity_key]
    return {
        "opportunity_key": opportunity_key,
        "prior_probability_percent": transition.success_probability * 100,
        "posterior_probability_percent": mean * 100,
        "conservative_probability_percent": lower * 100,
        "posterior_std_percent": std * 100,
        "raw_outcome_count": len(matching),
        "evidence_count": transition.evidence_count,
        "source_count": transition.source_count,
        "evidence_confidence_percent": transition.evidence_confidence * 100,
    }


def demo_uncertainty_metrics() -> dict:
    transition = MarketRouteTransition(
        name="Research monitor fixture", category="camera", currency="JPY",
        required_capital=10000, success_capital=18000, recovery_capital=6000,
        success_probability=0.75, evidence_confidence=0.8,
        estimated_days_to_sale=7, evidence_count=12, source_count=3,
    )
    outcomes = [SaleOutcome("monitor", True)] * 9 + [SaleOutcome("monitor", False)] * 3
    return uncertainty_metrics(transition, "monitor", outcomes)
