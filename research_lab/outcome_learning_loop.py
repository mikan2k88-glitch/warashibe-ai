"""Research-only closed loop from persisted outcomes to the next ranked decision."""

from research_lab.live_outcome_store import OutcomeStore
from research_lab.persisted_posterior_uncertainty_ranking import rank_from_store

LEARNING_LOOP_VERSION = "0.1"


def next_decision(candidates, store=None, credibility=0.90):
    """Rank current candidates from persisted feedback and return the best row.

    No outcome is fabricated or written here.  The caller supplies observed
    outcomes separately through OutcomeStore; this function only learns from
    what has already been persisted.
    """
    if not candidates:
        return None
    rows = rank_from_store(candidates, store or OutcomeStore(), credibility)
    return rows[0]
