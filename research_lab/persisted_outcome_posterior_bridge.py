"""Bridge persisted research outcomes into posterior route probabilities."""

from research_lab.live_outcome_store import OutcomeStore
from research_lab.posterior_route_integration import posterior_transition

BRIDGE_VERSION = "0.1"


def posterior_from_store(transition, opportunity_key, store=None, prior_strength=2.0):
    """Update a market transition from persisted outcomes for one opportunity."""
    store = store or OutcomeStore()
    return posterior_transition(
        transition,
        opportunity_key,
        store.for_opportunity(opportunity_key),
        prior_strength=prior_strength,
    )
