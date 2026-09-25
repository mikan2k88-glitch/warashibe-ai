"""Milestone validation for Warashibe AI real-world core integration.

Validates that the current milestone reaches HUMAN GATE from local fixtures
without granting any external or commercial execution authority.
"""

from research_lab.real_world_dry_run_pipeline import run_real_world_dry_run

WARASHIBE_CORE_MILESTONE_VALIDATION_VERSION = "0.1"

EXPECTED_MILESTONE = (
    "candidate_input",
    "core_boundary",
    "policy",
    "scoring",
    "route",
    "single_candidate",
    "human_gate",
)


def validate_real_world_core_milestone():
    dry_run = run_real_world_dry_run()
    result = dry_run.get("result", {})

    checks = {
        "dry_run_mode": dry_run.get("mode") == "real_world_dry_run",
        "candidate_input_present": dry_run.get("input_count", 0) > 0,
        "human_gate_reached": dry_run.get("reached_human_gate") is True,
        "terminal_status": result.get("status") == "ready_for_human_gate",
        "boundary_passed": result.get("boundary", {}).get("valid") is True,
        "policy_passed": result.get("policy", {}).get("allowed") is True,
        "scoring_passed": result.get("scoring", {}).get("eligible") is True,
        "single_candidate_selected": isinstance(result.get("candidate"), dict),
        "route_present": isinstance(result.get("route"), dict),
        "network_disabled": dry_run.get("network_execution_authorized") is False,
        "purchase_disabled": dry_run.get("purchase_authorized") is False,
        "listing_disabled": dry_run.get("listing_authorized") is False,
        "payment_disabled": dry_run.get("payment_authorized") is False,
        "refund_disabled": dry_run.get("refund_authorized") is False,
        "ledger_mutation_disabled": dry_run.get("ledger_mutation_authorized") is False,
        "external_action_disabled": dry_run.get("external_action_authorized") is False,
    }

    passed = all(checks.values())

    return {
        "version": WARASHIBE_CORE_MILESTONE_VALIDATION_VERSION,
        "milestone": "real_world_core_to_human_gate",
        "expected_flow": EXPECTED_MILESTONE,
        "passed": passed,
        "checks": checks,
        "selected_candidate": result.get("candidate"),
        "route_status": result.get("route", {}).get("status"),
        "terminal_status": result.get("status"),
        "execution_authorized": False,
        "commerce_authorized": False,
        "main_branch_change_authorized": False,
        "production_change_authorized": False,
    }
