"""Rank market transitions using persisted outcomes and posterior uncertainty."""

from research_lab.live_outcome_store import OutcomeStore
from research_lab.posterior_uncertainty_ranking import posterior_route_score

RANKING_VERSION = "0.1"


def score_from_store(transition, opportunity_key, store=None, credibility=0.90):
    """Score one transition using only outcomes persisted for its opportunity."""
    store = store or OutcomeStore()
    return posterior_route_score(
        transition,
        opportunity_key,
        store.for_opportunity(opportunity_key),
        credibility=credibility,
    )


def rank_from_store(candidates, store=None, credibility=0.90):
    """Return (key, transition, score) rows ordered from safest growth score down."""
    store = store or OutcomeStore()
    rows = [
        (key, transition, score_from_store(transition, key, store, credibility))
        for key, transition in candidates
    ]
    return sorted(rows, key=lambda row: row[2], reverse=True)
