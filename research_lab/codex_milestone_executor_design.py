"""Bounded milestone contract for future Codex execution.

Codex is treated as an implementation worker, not an authority boundary.
This module defines what Codex may change, how it must validate work, and
where it must stop. It does not invoke Codex or any external executor.
"""

CODEX_MILESTONE_EXECUTOR_DESIGN_VERSION = "0.1"

MILESTONE_ID = "sandbox_external_integration"

MILESTONE_GOAL = (
    "market_data_to_candidate_selection_to_gemini_orchestrator_to_human_gate_"
    "to_stripe_sandbox_event_to_ephemeral_ledger"
)

ALLOWED_BRANCHES = ("research-lab",)

FORBIDDEN_OPERATIONS = (
    "modify_main_branch",
    "modify_production_configuration",
    "read_or_modify_secrets",
    "invoke_live_gemini_without_gate",
    "invoke_live_stripe_without_gate",
    "purchase_item",
    "list_item",
    "send_payment",
    "issue_refund",
    "write_production_database",
    "delete_large_data_sets",
    "expand_privileges",
    "invoke_unbounded_external_executor",
)

REQUIRED_COMPLETION_CHECKS = (
    "market_data_adapter_present",
    "candidate_pipeline_present",
    "gemini_orchestrator_boundary_present",
    "human_gate_preserved",
    "stripe_sandbox_event_bridge_present",
    "ephemeral_ledger_present",
    "offline_integration_test_green",
    "latest_ci_green",
    "network_default_deny",
    "commerce_default_deny",
)

EXECUTION_LIMITS = {
    "max_cycles": 10,
    "max_repairs_per_cycle": 1,
    "one_theme_per_cycle": True,
    "require_ci_green_before_next_cycle": True,
    "stop_on_human_gate": True,
    "stop_on_unknown_capability": True,
}


def build_codex_milestone_contract():
    return {
        "version": CODEX_MILESTONE_EXECUTOR_DESIGN_VERSION,
        "mode": "design_only",
        "executor": "codex",
        "executor_role": "bounded_implementation_worker",
        "milestone_id": MILESTONE_ID,
        "milestone_goal": MILESTONE_GOAL,
        "allowed_branches": ALLOWED_BRANCHES,
        "forbidden_operations": FORBIDDEN_OPERATIONS,
        "required_completion_checks": REQUIRED_COMPLETION_CHECKS,
        "execution_limits": dict(EXECUTION_LIMITS),
        "implementation_loop": (
            "inspect_current_state",
            "select_smallest_missing_theme",
            "prepare_change",
            "run_offline_tests",
            "commit_research_lab_only",
            "inspect_ci",
            "repair_once_if_needed",
            "record_progress",
            "stop_when_milestone_complete",
        ),
        "human_gate_conditions": (
            "actual_codex_invocation",
            "network_or_secret_access",
            "live_external_api_call",
            "commerce_action",
            "production_change",
            "main_branch_change",
        ),
        "codex_invocation_authorized": False,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "external_action_authorized": False,
    }


def evaluate_milestone_completion(state):
    if not isinstance(state, dict):
        return {
            "complete": False,
            "missing": REQUIRED_COMPLETION_CHECKS,
            "codex_should_stop": True,
        }

    missing = tuple(
        check for check in REQUIRED_COMPLETION_CHECKS
        if state.get(check) is not True
    )

    return {
        "complete": not missing,
        "missing": missing,
        "codex_should_stop": not missing,
        "requires_human_review_before_external_activation": True,
    }


def validate_codex_milestone_contract():
    contract = build_codex_milestone_contract()
    assert contract["mode"] == "design_only"
    assert contract["executor"] == "codex"
    assert contract["allowed_branches"] == ("research-lab",)
    assert contract["execution_limits"]["max_cycles"] == 10
    assert contract["execution_limits"]["max_repairs_per_cycle"] == 1
    assert contract["execution_limits"]["require_ci_green_before_next_cycle"] is True
    assert contract["execution_limits"]["stop_on_human_gate"] is True
    assert contract["codex_invocation_authorized"] is False
    assert contract["network_execution_authorized"] is False
    assert contract["secret_access_authorized"] is False
    assert contract["commerce_authorized"] is False
    assert contract["production_change_authorized"] is False
    assert contract["main_branch_change_authorized"] is False
    assert contract["external_action_authorized"] is False
    return True
