"""Warashibe AI real-world engine stub.

This module connects research-lab candidate discovery/scoring outputs to the
core boundary. It stops before any external action. No network call, purchase,
listing, payment, refund, or production mutation is performed here.
"""

from warashibe_core_mode import (
    MODE_REAL_WORLD,
    build_core_mode_snapshot,
    validate_real_world_candidate_for_core,
)
from research_lab.real_world_candidate_scoring_design import (
    rank_candidates,
    score_candidate,
)

REAL_WORLD_ENGINE_VERSION = "0.1"


def prepare_real_world_candidate(candidate):
    boundary = validate_real_world_candidate_for_core(candidate)
    if not boundary["valid"]:
        return {
            "status": "rejected",
            "engine_version": REAL_WORLD_ENGINE_VERSION,
            "boundary": boundary,
            "scoring": None,
            "human_gate_required": True,
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    scoring = score_candidate(candidate)
    if not scoring.get("valid") or not scoring.get("eligible"):
        return {
            "status": "rejected",
            "engine_version": REAL_WORLD_ENGINE_VERSION,
            "boundary": boundary,
            "scoring": scoring,
            "human_gate_required": True,
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    return {
        "status": "ready_for_human_gate",
        "engine_version": REAL_WORLD_ENGINE_VERSION,
        "boundary": boundary,
        "scoring": scoring,
        "candidate": dict(candidate),
        "human_gate_required": True,
        "execution_authorized": False,
        "commerce_authorized": False,
    }


def select_real_world_candidate(candidates):
    ranked = rank_candidates(candidates)
    if not ranked:
        return {
            "status": "no_eligible_candidate",
            "engine_version": REAL_WORLD_ENGINE_VERSION,
            "selected": None,
            "human_gate_required": True,
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    selected = ranked[0]
    prepared = prepare_real_world_candidate(selected)
    prepared["ranked_count"] = len(ranked)
    return prepared


def build_real_world_engine_snapshot():
    core = build_core_mode_snapshot(MODE_REAL_WORLD)
    return {
        "version": REAL_WORLD_ENGINE_VERSION,
        "mode": MODE_REAL_WORLD,
        "core": core,
        "flow": (
            "receive_normalized_candidates",
            "core_boundary_validation",
            "candidate_scoring",
            "single_candidate_selection",
            "prepare_human_gate",
            "stop_before_external_action",
        ),
        "market_network_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "refund_authorized": False,
        "ledger_mutation_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
    }
