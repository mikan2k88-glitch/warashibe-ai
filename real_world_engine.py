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
from real_world_policy_bridge import evaluate_real_world_policy
from real_world_route_bridge import evaluate_real_world_routes

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

    policy = evaluate_real_world_policy(candidate)
    if not policy.get("allowed"):
        return {
            "status": "rejected",
            "engine_version": REAL_WORLD_ENGINE_VERSION,
            "boundary": boundary,
            "policy": policy,
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
            "policy": policy,
            "scoring": scoring,
            "human_gate_required": True,
            "execution_authorized": False,
            "commerce_authorized": False,
        }

    return {
        "status": "ready_for_human_gate",
        "engine_version": REAL_WORLD_ENGINE_VERSION,
        "boundary": boundary,
        "policy": policy,
        "scoring": scoring,
        "candidate": dict(candidate),
        "human_gate_required": True,
        "execution_authorized": False,
        "commerce_authorized": False,
    }


def select_real_world_candidate(candidates, route_ladder=None, target_jpy=1_000_000):
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

    scoring_by_item_id = {
        row.get("item_id"): row.get("scoring", {})
        for row in ranked
        if row.get("item_id")
    }
    initial_capital = (
        ranked[0]["purchase_price_jpy"]
        + ranked[0]["estimated_fees_jpy"]
        + ranked[0]["estimated_shipping_jpy"]
    )
    route = evaluate_real_world_routes(
        initial_capital,
        ranked,
        scoring_by_item_id=scoring_by_item_id,
        route_ladder=route_ladder,
        target_jpy=target_jpy,
    )

    if route["route_data_complete"] and route["candidates"]:
        best_route = route["candidates"][0]
        selected_id = best_route.get("item_id")
        selected = next(
            (row for row in ranked if row.get("item_id") == selected_id),
            ranked[0],
        )
    else:
        selected = ranked[0]

    prepared = prepare_real_world_candidate(selected)
    prepared["ranked_count"] = len(ranked)
    prepared["route"] = route
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
            "policy_validation",
            "candidate_scoring",
            "route_evaluation",
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
