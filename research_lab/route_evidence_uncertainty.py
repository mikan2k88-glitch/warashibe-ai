"""Evidence-aware uncertainty layer for observed real-market route transitions.

Research only. It creates a conservative probability band around the nominal
sale probability using evidence confidence. This is a lightweight precursor to
a formal robust-MDP ambiguity set; it does not alter the production Route Engine.
"""

from dataclasses import dataclass

from research_lab.real_market_route_bridge import MarketRouteTransition

UNCERTAINTY_VERSION = "0.1"
MAX_PROBABILITY_RADIUS = 0.25


@dataclass(frozen=True)
class UncertainMarketRouteTransition:
    transition: MarketRouteTransition
    probability_low: float
    probability_nominal: float
    probability_high: float
    probability_radius: float


def probability_radius(evidence_confidence: float) -> float:
    confidence = max(0.0, min(1.0, float(evidence_confidence)))
    return MAX_PROBABILITY_RADIUS * (1.0 - confidence)


def add_evidence_uncertainty(
    transition: MarketRouteTransition,
) -> UncertainMarketRouteTransition:
    nominal = max(0.0, min(1.0, transition.success_probability))
    radius = probability_radius(transition.evidence_confidence)
    return UncertainMarketRouteTransition(
        transition=transition,
        probability_low=max(0.0, nominal - radius),
        probability_nominal=nominal,
        probability_high=min(1.0, nominal + radius),
        probability_radius=radius,
    )


def conservative_route_score(transition: MarketRouteTransition) -> float:
    """Simple research score: downside probability × capital growth."""
    uncertain = add_evidence_uncertainty(transition)
    growth = transition.success_capital / transition.required_capital
    return uncertain.probability_low * growth
