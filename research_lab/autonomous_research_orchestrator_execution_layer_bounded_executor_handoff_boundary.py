"""Build an inert handoff boundary for one bounded research cycle.

The handoff boundary accepts only a validated open cycle boundary and emits a
local request description. It never invokes the executor or performs repository
or external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_cycle_boundary import (
    build_bounded_executor_cycle_boundary,
)
from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_cycle_boundary_validation import (
    validate_bounded_executor_cycle_boundary_output,
)

BOUNDED_EXECUTOR_HANDOFF_BOUNDARY_VERSION = "0.1"


def build_bounded_executor_handoff_boundary(
    cycles_completed=0,
    ci_status="success",
    repair_attempts=0,
    human_gate_required=False,
    milestone_reached=False,
    branch="research-lab",
):
    boundary = build_bounded_executor_cycle_boundary(
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
        human_gate_required=human_gate_required,
        milestone_reached=milestone_reached,
        branch=branch,
    )
    validation = validate_bounded_executor_cycle_boundary_output(boundary)
    ready = (
        validation["valid"] is True
        and validation["ready_for_executor_handoff_boundary"] is True
    )

    requests = tuple(
        {
            "step": step,
            "requested": True,
            "performed": False,
            "external_action_authorized": False,
        }
        for step in boundary["planned_steps"]
    ) if ready else ()

    return {
        "version": BOUNDED_EXECUTOR_HANDOFF_BOUNDARY_VERSION,
        "handoff_valid": validation["valid"] is True,
        "handoff_ready": ready,
        "branch": boundary["branch"],
        "research_branch_only": boundary["research_branch_only"],
        "cycles_completed_before": boundary["cycles_completed_before"],
        "cycles_completed_after_plan": boundary["cycles_completed_after_plan"],
        "requests": requests,
        "request_count": len(requests),
        "reason": "bounded_executor_handoff_ready" if ready else boundary["reason"],
        "executor_invocation_authorized": False,
        "executor_invoked": False,
        "main_branch_authorized": False,
        "credentials_change_authorized": False,
        "production_change_authorized": False,
        "commerce_authorized": False,
        "notification_authorized": False,
        "external_action_authorized": False,
        "external_action_performed": False,
    }


def validate_bounded_executor_handoff_boundary():
    ready = build_bounded_executor_handoff_boundary(cycles_completed=9, repair_attempts=1)
    assert ready["handoff_valid"] is True
    assert ready["handoff_ready"] is True
    assert ready["cycles_completed_after_plan"] == 10
    assert ready["request_count"] == 7
    assert all(request["performed"] is False for request in ready["requests"])
    assert ready["executor_invocation_authorized"] is False

    exhausted = build_bounded_executor_handoff_boundary(cycles_completed=10)
    assert exhausted["handoff_ready"] is False
    assert exhausted["requests"] == ()

    gated = build_bounded_executor_handoff_boundary(human_gate_required=True)
    assert gated["handoff_ready"] is False

    milestone = build_bounded_executor_handoff_boundary(milestone_reached=True)
    assert milestone["handoff_ready"] is False

    assert build_bounded_executor_handoff_boundary(branch="main")["handoff_ready"] is False
    assert build_bounded_executor_handoff_boundary(ci_status="failure")["handoff_ready"] is False
    return True
