"""Design bounded activation for a future autonomous research executor.

This is local activation policy data only. It does not invoke GitHub or any
external system. Approved scope remains research-lab and bounded milestones.
"""

EXECUTOR_ACTIVATION_DESIGN_VERSION = "0.1"
MAX_AUTONOMOUS_CYCLES = 10
ALLOWED_BRANCH = "research-lab"

BLOCKED_CAPABILITIES = (
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


def executor_activation_design(branch=ALLOWED_BRANCH, max_cycles=MAX_AUTONOMOUS_CYCLES):
    valid_cycles = (
        isinstance(max_cycles, int)
        and not isinstance(max_cycles, bool)
        and 1 <= max_cycles <= MAX_AUTONOMOUS_CYCLES
    )
    scope_valid = branch == ALLOWED_BRANCH and valid_cycles

    return {
        "version": EXECUTOR_ACTIVATION_DESIGN_VERSION,
        "activation_design_valid": scope_valid,
        "branch": branch,
        "max_autonomous_cycles": max_cycles if valid_cycles else None,
        "milestone_bounded": True,
        "requires_green_ci": True,
        "max_repair_attempts_per_cycle": 1,
        "stop_on_unknown_action": True,
        "stop_on_human_gate": True,
        "blocked_capabilities": BLOCKED_CAPABILITIES,
        "executor_activation_authorized": scope_valid,
        "external_action_scope": "research_branch_only" if scope_valid else "none",
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
    }


def validate_executor_activation_design():
    design = executor_activation_design()
    assert design["activation_design_valid"] is True
    assert design["executor_activation_authorized"] is True
    assert design["branch"] == "research-lab"
    assert design["max_autonomous_cycles"] == 10
    assert design["stop_on_human_gate"] is True

    assert executor_activation_design(branch="main")["executor_activation_authorized"] is False
    assert executor_activation_design(max_cycles=11)["executor_activation_authorized"] is False
    assert executor_activation_design(max_cycles=True)["executor_activation_authorized"] is False
    return True
