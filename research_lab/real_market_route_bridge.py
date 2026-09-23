"""Research-only bridge from real-market estimates to route-ready transitions.

The bridge does not invent a complete market graph. Each MarketEstimate becomes
one observed action available only when its purchase price is affordable.
Production Route Engine remains unchanged.
"""

from dataclasses import dataclass

from research_lab.market_evidence_estimator import MarketEstimate

BRIDGE_VERSION = "0.1"


@dataclass(frozen=True)
class MarketRouteTransition:
    name: str
    category: str
    currency: str
    required_capital: float
    success_capital: float
    recovery_capital: float
    success_probability: float
    evidence_confidence: float
    estimated_days_to_sale: float | None
    evidence_count: int
    source_count: int


def estimate_to_transition(estimate: MarketEstimate) -> MarketRouteTransition:
    recovery = 0.0 if estimate.recovery_value is None else max(0.0, float(estimate.recovery_value))
    return MarketRouteTransition(
        name=estimate.name,
        category=estimate.category,
        currency=estimate.currency,
        required_capital=float(estimate.purchase_price),
        success_capital=float(estimate.expected_sale_price),
        recovery_capital=recovery,
        success_probability=max(0.0, min(1.0, float(estimate.sale_probability))),
        evidence_confidence=max(0.0, min(1.0, float(estimate.confidence))),
        estimated_days_to_sale=estimate.estimated_days_to_sale,
        evidence_count=estimate.evidence_count,
        source_count=estimate.source_count,
    )


def available_transitions(estimates: list[MarketEstimate], current_capital: float) -> list[MarketRouteTransition]:
    """Return only observed transitions affordable from current capital."""
    transitions = [
        estimate_to_transition(estimate)
        for estimate in estimates
        if 0 < estimate.purchase_price <= current_capital
        and estimate.expected_sale_price > estimate.purchase_price
    ]
    return sorted(
        transitions,
        key=lambda x: (
            x.evidence_confidence,
            x.success_probability,
            x.success_capital,
        ),
        reverse=True,
    )


def route_snapshot(estimates: list[MarketEstimate], current_capital: float) -> dict:
    transitions = available_transitions(estimates, current_capital)
    return {
        "version": BRIDGE_VERSION,
        "current_capital": current_capital,
        "observed_transition_count": len(transitions),
        "transitions": transitions,
        "graph_complete": False,
        "note": "Observed market opportunities only; missing future-capital opportunities are not inferred.",
    }
