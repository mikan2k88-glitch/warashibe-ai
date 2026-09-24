"""Control bounded activation state for the autonomous research executor.

The controller is pure and local. It records whether activation may enter a
ready state; it does not invoke GitHub or any external executor.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_policy import (
    evaluate_executor_activation,
)

EXECUTOR_ACTIVATION_CONTROLLER_VERSION = "0.1"


def control_executor_activation(branch="research-lab", max_cycles=10,
                                ci_status="success", human_gate_approved=False):
    policy = evaluate_executor_activation(
        branch=branch,
        max_cycles=max_cycles,
        ci_status=ci_status,
        human_gate_approved=human_gate_approved,
    )
    ready = policy["allowed"] is True

    return {
        "version": EXECUTOR_ACTIVATION_CONTROLLER_VERSION,
        "state": "ready" if ready else "stopped",
        "executor_ready": ready,
        "reason": policy["reason"],
        "branch": policy["branch"],
        "max_autonomous_cycles": policy["max_autonomous_cycles"],
        "cycles_completed": 0,
        "milestone_bounded": policy["milestone_bounded"],
        "research_branch_only": policy["research_branch_only"],
        "requires_green_ci": policy["requires_green_ci"],
        "human_gate_approved": policy["human_gate_approved"],
        "executor_invoked": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
    }


def validate_executor_activation_controller():
    ready = control_executor_activation(human_gate_approved=True)
    assert ready["state"] == "ready"
    assert ready["executor_ready"] is True
    assert ready["cycles_completed"] == 0
    assert ready["executor_invoked"] is False

    stopped = control_executor_activation()
    assert stopped["state"] == "stopped"
    assert stopped["executor_ready"] is False

    failed_ci = control_executor_activation(
        ci_status="failure", human_gate_approved=True
    )
    assert failed_ci["executor_ready"] is False
    return True
