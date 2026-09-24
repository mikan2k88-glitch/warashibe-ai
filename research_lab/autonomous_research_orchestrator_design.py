"""Safety contract for a future autonomous research orchestrator.

The orchestrator may automate bounded research work on research-lab, but it
must stop before production, financial, credential, or real-world mutations.
This module defines policy only; it performs no external action.
"""

ORCHESTRATOR_DESIGN_VERSION = "0.1"

AUTONOMOUS_ACTIONS = (
    "inspect_research_state",
    "select_small_next_theme",
    "edit_research_lab_code",
    "add_or_update_tests",
    "run_offline_tests",
    "inspect_ci_result",
    "repair_failed_research_ci",
    "record_next_theme",
)

HUMAN_GATE_ACTIONS = (
    "modify_main_branch",
    "execute_supabase_ddl",
    "change_secrets_or_credentials",
    "change_billing_or_paid_plan",
    "change_external_production_config",
    "purchase_real_item",
    "sell_real_item",
    "execute_payment",
)

STOP_CONDITIONS = (
    "ambiguous_scope",
    "unfixable_tests",
    "api_compatibility_risk",
    "security_privilege_expansion",
    "destructive_operation",
    "large_or_irreversible_change",
)


def classify_action(action):
    if action in AUTONOMOUS_ACTIONS:
        return "autonomous"
    if action in HUMAN_GATE_ACTIONS:
        return "human_gate"
    return "stop_unknown"


def validate_orchestrator_design():
    assert not set(AUTONOMOUS_ACTIONS).intersection(HUMAN_GATE_ACTIONS)
    assert classify_action("edit_research_lab_code") == "autonomous"
    assert classify_action("modify_main_branch") == "human_gate"
    assert classify_action("execute_supabase_ddl") == "human_gate"
    assert classify_action("execute_payment") == "human_gate"
    assert classify_action("undefined_action") == "stop_unknown"
    return True
