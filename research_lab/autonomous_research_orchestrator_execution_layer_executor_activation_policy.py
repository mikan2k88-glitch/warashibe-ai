"""Evaluate whether the bounded research executor may enter active mode.

Policy is fail-closed and only authorizes the research-lab execution scope.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_design import (
    ALLOWED_BRANCH,
    MAX_AUTONOMOUS_CYCLES,
    executor_activation_design,
)

EXECUTOR_ACTIVATION_POLICY_VERSION = "0.1"


def evaluate_executor_activation(branch=ALLOWED_BRANCH, max_cycles=MAX_AUTONOMOUS_CYCLES,
                                 ci_status="success", human_gate_approved=False):
    design = executor_activation_design(branch=branch, max_cycles=max_cycles)
    gate_valid = human_gate_approved is True
    ci_green = ci_status == "success"
    allowed = (
        design["activation_design_valid"] is True
        and design["executor_activation_authorized"] is True
        and gate_valid
        and ci_green
    )

    if not design["activation_design_valid"]:
        reason = "activation_design_invalid"
    elif not gate_valid:
        reason = "human_gate_not_approved"
    elif not ci_green:
        reason = "ci_not_green"
    else:
        reason = "bounded_executor_activation_allowed"

    return {
        "version": EXECUTOR_ACTIVATION_POLICY_VERSION,
        "allowed": allowed,
        "reason": reason,
        "branch": branch,
        "max_autonomous_cycles": design["max_autonomous_cycles"],
        "milestone_bounded": True,
        "research_branch_only": branch == ALLOWED_BRANCH,
        "requires_green_ci": True,
        "human_gate_approved": gate_valid,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
    }


def validate_executor_activation_policy():
    allowed = evaluate_executor_activation(human_gate_approved=True)
    assert allowed["allowed"] is True
    assert allowed["reason"] == "bounded_executor_activation_allowed"

    assert evaluate_executor_activation()["allowed"] is False
    assert evaluate_executor_activation(branch="main", human_gate_approved=True)["allowed"] is False
    assert evaluate_executor_activation(ci_status="failure", human_gate_approved=True)["allowed"] is False
    assert evaluate_executor_activation(max_cycles=11, human_gate_approved=True)["allowed"] is False
    return True
