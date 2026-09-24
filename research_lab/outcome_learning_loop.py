"""Research-only closed loop from persisted outcomes to the next ranked decision."""

from research_lab.outcome_repository_factory import build_outcome_repository
from research_lab.persisted_posterior_uncertainty_ranking import rank_from_store

LEARNING_LOOP_VERSION = "0.3"


def repository_observability(store=None, *, backend="json", path=None,
                             supabase_client=None, table="warashibe_sale_outcomes"):
    """Return backend-neutral storage health without exposing credentials or rows."""
    repository = store or build_outcome_repository(
        backend, path=path, supabase_client=supabase_client, table=table
    )
    stats = repository.stats()
    return {
        "backend": "injected" if store is not None else (backend or "json").strip().lower(),
        "mode": stats.get("mode", "unknown"),
        "total": int(stats.get("total", 0)),
        "sold": int(stats.get("sold", 0)),
        "failed": int(stats.get("failed", 0)),
        "opportunities": int(stats.get("opportunities", 0)),
    }


def next_decision(candidates, store=None, credibility=0.90, *, backend="json", path=None,
                  supabase_client=None, table="warashibe_sale_outcomes"):
    """Rank current candidates from persisted feedback and return the best row.

    Existing callers may still inject ``store`` directly.  When omitted, the
    repository factory selects the backend; JSON remains the safe default and
    Supabase requires an explicitly injected client.
    """
    if not candidates:
        return None
    repository = store or build_outcome_repository(
        backend, path=path, supabase_client=supabase_client, table=table
    )
    rows = rank_from_store(candidates, repository, credibility)
    return rows[0]
