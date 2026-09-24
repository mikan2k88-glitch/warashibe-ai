"""Closed-loop research cycle: fresh market evidence -> decision -> observed outcome -> learning.

The market phase is read-only. Outcomes are recorded only when explicitly
provided by the caller; no purchase, sale, payment, or success is inferred.
"""

from research_lab.conflict_aware_evidence_grouping import estimate_conflict_aware
from research_lab.decision_outcome_learning_bridge import (
    learned_next_decision,
    opportunity_key,
    record_observed_outcome,
)
from research_lab.market_estimate_quality_gate import evaluate_market_estimate
from research_lab.market_snapshot_freshness import filter_fresh_observations
from research_lab.multi_provider_market_snapshot import capture_market_snapshot

CLOSED_LOOP_VERSION = "0.1"


def observe_market(providers, query, *, max_age_seconds=3600, now=None, **gate_kwargs):
    snapshot = capture_market_snapshot(providers, query)
    freshness = filter_fresh_observations(
        snapshot.observations, now=now, max_age_seconds=max_age_seconds
    )
    estimates = estimate_conflict_aware(freshness.accepted)
    accepted, rejected = [], []
    for estimate in estimates:
        gate = evaluate_market_estimate(estimate, **gate_kwargs)
        if gate.accepted:
            accepted.append(estimate)
        else:
            rejected.append((estimate, gate.reasons))
    return {
        "version": CLOSED_LOOP_VERSION,
        "snapshot": snapshot,
        "freshness": freshness,
        "estimates": estimates,
        "accepted_estimates": accepted,
        "rejected_estimates": rejected,
    }


def choose_with_learning(observation, repository, credibility=0.90):
    estimates = observation["accepted_estimates"]
    if not estimates:
        return None
    return learned_next_decision(estimates, repository, credibility)


def record_cycle_outcome(observation, repository, selected_key, *, sold, days_to_outcome=None):
    """Attach an explicit outcome only to an opportunity present in this cycle."""
    matches = [
        estimate for estimate in observation["accepted_estimates"]
        if opportunity_key(estimate) == selected_key
    ]
    if len(matches) != 1:
        raise ValueError("selected_key must identify exactly one accepted opportunity")
    return record_observed_outcome(
        repository, matches[0], sold=sold, days_to_outcome=days_to_outcome
    )
