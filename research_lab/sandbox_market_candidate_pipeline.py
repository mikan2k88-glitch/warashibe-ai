"""Offline market-record -> real-world candidate selection pipeline.

This pipeline normalizes already-fetched market records, passes candidates into
the real-world engine, and stops at HUMAN GATE. It performs no network calls,
purchases, listings, payments, or persistent ledger writes.
"""

from research_lab.sandbox_market_data_adapter_design import build_market_data_batch
from real_world_engine import select_real_world_candidate

SANDBOX_MARKET_CANDIDATE_PIPELINE_VERSION = "0.1"


def run_sandbox_market_candidate_pipeline(records, route_ladder=None, target_jpy=1_000_000):
    batch = build_market_data_batch(records)
    candidates = list(batch["normalized"])

    if not candidates:
        return {
            "version": SANDBOX_MARKET_CANDIDATE_PIPELINE_VERSION,
            "mode": "offline_market_candidate_pipeline",
            "status": "no_valid_market_candidates",
            "market_batch": batch,
            "selection": None,
            "reached_human_gate": False,
            "network_execution_authorized": False,
            "purchase_authorized": False,
            "listing_authorized": False,
            "payment_authorized": False,
            "persistent_ledger_write_authorized": False,
            "external_action_authorized": False,
        }

    selection = select_real_world_candidate(
        candidates,
        route_ladder=route_ladder,
        target_jpy=target_jpy,
    )

    return {
        "version": SANDBOX_MARKET_CANDIDATE_PIPELINE_VERSION,
        "mode": "offline_market_candidate_pipeline",
        "status": selection.get("status"),
        "market_batch": batch,
        "selection": selection,
        "reached_human_gate": selection.get("status") == "ready_for_human_gate",
        "normalized_count": batch["normalized_count"],
        "rejected_count": batch["rejected_count"],
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "persistent_ledger_write_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }


def build_sandbox_market_candidate_pipeline_snapshot():
    return {
        "version": SANDBOX_MARKET_CANDIDATE_PIPELINE_VERSION,
        "mode": "offline_market_candidate_pipeline",
        "flow": (
            "receive_market_records",
            "normalize_market_records",
            "core_boundary_validation",
            "policy_validation",
            "candidate_scoring",
            "route_evaluation",
            "single_candidate_selection",
            "stop_at_human_gate",
        ),
        "network_execution_authorized": False,
        "purchase_authorized": False,
        "listing_authorized": False,
        "payment_authorized": False,
        "persistent_ledger_write_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
