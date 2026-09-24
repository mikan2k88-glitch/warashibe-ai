"""Freshness-gated multi-provider market decision flow."""

from research_lab.conflict_aware_evidence_grouping import estimate_conflict_aware
from research_lab.market_snapshot_freshness import filter_fresh_observations
from research_lab.multi_provider_market_snapshot import capture_market_snapshot
from research_lab.quality_gated_candidate_pipeline import evaluate_quality_gated_estimates

FRESH_DECISION_VERSION = "0.1"


def run_fresh_multi_provider_decision(
    providers, query, current_capital, *, max_age_seconds=3600, now=None, **gate_kwargs
):
    snapshot = capture_market_snapshot(providers, query)
    freshness = filter_fresh_observations(
        snapshot.observations, now=now, max_age_seconds=max_age_seconds
    )
    estimates = estimate_conflict_aware(freshness.accepted)
    decision = evaluate_quality_gated_estimates(estimates, current_capital, **gate_kwargs)
    decision.update({
        "fresh_decision_version": FRESH_DECISION_VERSION,
        "snapshot_provider_count": snapshot.provider_count,
        "snapshot_raw_count": snapshot.raw_count,
        "fresh_observations": len(freshness.accepted),
        "stale_observations": freshness.stale,
        "invalid_timestamp_observations": freshness.missing_timestamp,
    })
    return decision
