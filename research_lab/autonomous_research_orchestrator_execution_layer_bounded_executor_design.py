"""Design a bounded autonomous research executor scope.

This module defines local execution constraints only. It does not invoke GitHub,
modify repositories, or perform any external action.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_cycle_plan import (
    CANONICAL_CYCLE_STEPS,
)

BOUNDED_EXECUTOR_DESIGN_VERSION = "0.1"
ALLOWED_BRANCH = "research-lab"
MAX_AUTONOMOUS_CYCLES = 10
MAX_REPAIR_ATTEMPTS_PER_CYCLE = 1


def bounded_executor_design(branch=ALLOWED_BRANCH, max_cycles=MAX_AUTONOMOUS_CYCLES):
    valid_cycles = (
        isinstance(max_cycles, int)
        and not isinstance(max_cycles, bool)
        and 1 <= max_cycles <= MAX_AUTONOMOUS_CYCLES
    )
    valid = branch == ALLOWED_BRANCH and valid_cycles

    return {
        "version": BOUNDED_EXECUTOR_DESIGN_VERSION,
        "design_valid": valid,
        "branch": branch,
        "research_branch_only": branch == ALLOWED_BRANCH,
        "max_autonomous_cycles": max_cycles if valid_cycles else None,
        "canonical_cycle_steps": CANONICAL_CYCLE_STEPS,
        "one_theme_per_cycle": True,
        "requires_green_ci": True,
        "max_repair_attempts_per_cycle": MAX_REPAIR_ATTEMPTS_PER_CYCLE,
        "stop_on_human_gate": True,
        "stop_on_unknown_action": True,
        "stop_at_milestone": True,
        "milestone_bounded": True,
        "executor_invocation_authorized": False,
        "executor_invoked": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
        "external_action_authorized": False,
    }


def validate_bounded_executor_design():
    design = bounded_executor_design()
    assert design["design_valid"] is True
    assert design["branch"] == "research-lab"
    assert design["max_autonomous_cycles"] == 10
    assert design["one_theme_per_cycle"] is True
    assert design["max_repair_attempts_per_cycle"] == 1
    assert design["stop_on_human_gate"] is True
    assert design["executor_invocation_authorized"] is False
    assert design["external_action_authorized"] is False

    assert bounded_executor_design(branch="main")["design_valid"] is False
    assert bounded_executor_design(max_cycles=11)["design_valid"] is False
    assert bounded_executor_design(max_cycles=True)["design_valid"] is False
    return True
