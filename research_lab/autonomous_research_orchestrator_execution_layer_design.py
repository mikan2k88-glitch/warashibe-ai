"""Define the safe local contract for an autonomous research execution layer.

This module describes what a future executor may request. It performs no GitHub,
network, credential, production, commerce, or external notification action.
"""

EXECUTION_LAYER_DESIGN_VERSION = "0.1"
DEFAULT_MAX_AUTONOMOUS_CYCLES = 10

AUTONOMOUS_STEPS = (
    "inspect_state",
    "select_next_theme",
    "prepare_small_change",
    "run_offline_tests",
    "request_research_branch_commit",
    "inspect_ci",
    "record_progress",
)

HUMAN_GATE_STEPS = (
    "modify_main_branch",
    "change_secrets_or_credentials",
    "change_billing_or_paid_plan",
    "change_external_production_config",
    "execute_supabase_ddl",
    "expand_security_privileges",
    "perform_destructive_data_operation",
    "purchase_real_item",
    "sell_real_item",
    "execute_payment",
    "send_external_notification",
)


def execution_layer_design(max_cycles=DEFAULT_MAX_AUTONOMOUS_CYCLES):
    valid_limit = isinstance(max_cycles, int) and not isinstance(max_cycles, bool) and 1 <= max_cycles <= DEFAULT_MAX_AUTONOMOUS_CYCLES
    return {
        "version": EXECUTION_LAYER_DESIGN_VERSION,
        "design_valid": valid_limit,
        "max_autonomous_cycles": max_cycles if valid_limit else 0,
        "autonomous_steps": AUTONOMOUS_STEPS,
        "human_gate_steps": HUMAN_GATE_STEPS,
        "research_branch_only": True,
        "requires_green_ci_before_next_cycle": True,
        "max_repair_attempts_per_cycle": 1,
        "external_action_authorized": False,
        "external_action_performed": False,
        "credentials_included": False,
        "production_changed": False,
        "commerce_executed": False,
    }


def classify_execution_step(step):
    if step in AUTONOMOUS_STEPS:
        return "autonomous"
    if step in HUMAN_GATE_STEPS:
        return "human_gate"
    return "stop_unknown"


def validate_execution_layer_design():
    design = execution_layer_design()
    assert design["design_valid"] is True
    assert design["max_autonomous_cycles"] == 10
    assert design["research_branch_only"] is True
    assert design["external_action_authorized"] is False
    assert classify_execution_step("inspect_ci") == "autonomous"
    assert classify_execution_step("modify_main_branch") == "human_gate"
    assert classify_execution_step("undefined_step") == "stop_unknown"

    invalid = execution_layer_design(11)
    assert invalid["design_valid"] is False
    assert invalid["max_autonomous_cycles"] == 0
    return True
