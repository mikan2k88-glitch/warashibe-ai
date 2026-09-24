"""Control one bounded autonomous research cycle locally.

The controller composes bounded-executor policy into a ready/stopped decision.
It does not invoke an executor, mutate a repository, or perform external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_policy import (
    evaluate_bounded_executor_cycle,
)

BOUNDED_EXECUTOR_CONTROLLER_VERSION = "0.1"


def control_bounded_executor_cycle(
    cycles_completed=0,
    ci_status="success",
    repair_attempts=0,
    human_gate_required=False,
    milestone_reached=False,
    branch="research-lab",
):
    policy = evaluate_bounded_executor_cycle(
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
        human_gate_required=human_gate_required,
        milestone_reached=milestone_reached,
        branch=branch,
    )
    ready = policy["allowed"] is True

    return {
        "version": BOUNDED_EXECUTOR_CONTROLLER_VERSION,
        "state": "ready" if ready else "stopped",
        "cycle_ready": ready,
        "continue_autonomous_research": ready,
        "reason": policy["reason"],
        "branch": policy["branch"],
        "research_branch_only": policy["research_branch_only"],
        "cycles_completed": policy["cycles_completed"],
        "max_autonomous_cycles": policy["max_autonomous_cycles"],
        "repair_attempts": policy["repair_attempts"],
        "max_repair_attempts_per_cycle": policy["max_repair_attempts_per_cycle"],
        "requires_green_ci": policy["requires_green_ci"],
        "human_gate_required": policy["human_gate_required"],
        "milestone_reached": policy["milestone_reached"],
        "executor_invocation_authorized": False,
        "executor_invoked": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
        "external_action_authorized": False,
    }


def validate_bounded_executor_controller():
    ready = control_bounded_executor_cycle(cycles_completed=9, repair_attempts=1)
    assert ready["state"] == "ready"
    assert ready["cycle_ready"] is True
    assert ready["cycles_completed"] == 9
    assert ready["executor_invocation_authorized"] is False
    assert ready["executor_invoked"] is False

    exhausted = control_bounded_executor_cycle(cycles_completed=10)
    assert exhausted["state"] == "stopped"
    assert exhausted["continue_autonomous_research"] is False

    gated = control_bounded_executor_cycle(human_gate_required=True)
    assert gated["state"] == "stopped"
    assert gated["human_gate_required"] is True

    milestone = control_bounded_executor_cycle(milestone_reached=True)
    assert milestone["state"] == "stopped"

    assert control_bounded_executor_cycle(branch="main")["cycle_ready"] is False
    assert control_bounded_executor_cycle(ci_status="failure")["cycle_ready"] is False
    return True
