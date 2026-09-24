"""Bridge a market decision cycle to the persisted outcome learning loop.

This does not fabricate outcomes. A completed sale/failure must be supplied
explicitly before it is appended to the repository.
"""

from research_lab.outcome_learning_loop import next_decision
from research_lab.raw_outcome_calibration import SaleOutcome
from research_lab.real_market_route_bridge import estimate_to_transition

DECISION_LEARNING_BRIDGE_VERSION = "0.1"


def opportunity_key(estimate) -> str:
    return f"{estimate.currency}:{estimate.category}:{estimate.name}".strip().casefold()


def record_observed_outcome(repository, estimate, *, sold: bool, days_to_outcome=None) -> int:
    """Persist one explicit observed result; never infer success from a decision."""
    outcome = SaleOutcome(
        opportunity_key=opportunity_key(estimate),
        sold=bool(sold),
        days_to_outcome=days_to_outcome,
    )
    return repository.append(outcome)


def learned_next_decision(estimates, repository, credibility=0.90):
    """Rank current market estimates using persisted observed outcomes."""
    candidates = [
        (opportunity_key(estimate), estimate_to_transition(estimate))
        for estimate in estimates
    ]
    return next_decision(candidates, store=repository, credibility=credibility)
