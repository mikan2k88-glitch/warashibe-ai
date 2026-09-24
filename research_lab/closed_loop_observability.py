"""Dashboard-safe observability for the closed market-learning loop."""

from research_lab.live_outcome_store import OutcomeStore
from research_lab.outcome_learning_loop import repository_observability

OBSERVABILITY_VERSION = "0.1"


def closed_loop_observability(*, snapshot=None, freshness=None, estimates=None,
                              accepted_estimates=None, rejected_estimates=None,
                              store=None):
    """Return aggregate metrics only; never expose credentials or raw outcome rows."""
    snapshot = snapshot or {}
    freshness = freshness or {}
    estimates = estimates or []
    accepted_estimates = accepted_estimates or []
    rejected_estimates = rejected_estimates or []
    repository = store or OutcomeStore()

    def attr(obj, name, default=0):
        return getattr(obj, name, default) if obj is not None else default

    return {
        "version": OBSERVABILITY_VERSION,
        "market": {
            "providers": attr(snapshot, "provider_count"),
            "raw_evidence": attr(snapshot, "raw_count"),
            "normalized_evidence": len(attr(snapshot, "observations", ()) or ()),
            "fresh_evidence": len(attr(freshness, "accepted", ()) or ()),
            "stale_evidence": attr(freshness, "stale"),
            "invalid_timestamp": attr(freshness, "missing_timestamp"),
        },
        "quality": {
            "estimates": len(estimates),
            "accepted": len(accepted_estimates),
            "rejected": len(rejected_estimates),
        },
        "learning": repository_observability(store=repository),
    }


def empty_closed_loop_observability(store=None):
    return closed_loop_observability(store=store)
