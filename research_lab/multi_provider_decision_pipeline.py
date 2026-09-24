"""End-to-end decision from a synchronized multi-provider evidence snapshot."""

from research_lab.conflict_aware_evidence_grouping import estimate_conflict_aware
from research_lab.multi_provider_market_snapshot import capture_market_snapshot
from research_lab.quality_gated_candidate_pipeline import evaluate_quality_gated_estimates

MULTI_PROVIDER_DECISION_VERSION = "0.1"


def run_multi_provider_decision(providers, query, current_capital, **gate_kwargs):
    snapshot = capture_market_snapshot(providers, query)
    estimates = estimate_conflict_aware(snapshot.observations)
    decision = evaluate_quality_gated_estimates(estimates, current_capital, **gate_kwargs)
    decision["multi_provider_decision_version"] = MULTI_PROVIDER_DECISION_VERSION
    decision["snapshot_captured_at"] = snapshot.captured_at
    decision["snapshot_provider_count"] = snapshot.provider_count
    decision["snapshot_raw_count"] = snapshot.raw_count
    decision["snapshot_rejected_count"] = snapshot.rejected_count
    return decision
