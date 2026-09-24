"""Define the inert boundary for one bounded autonomous research cycle.

The boundary combines controller validation with the canonical cycle plan and
emits only a local handoff description. It never invokes the executor or
performs repository or external actions.
"""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_controller import (
    control_bounded_executor_cycle,
)
from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_controller_validation import (
    validate_bounded_executor_controller_output,
)
from research_lab.autonomous_research_orchestrator_execution_layer_cycle_plan import (
    build_execution_cycle_plan,
)

BOUNDED_EXECUTOR_CYCLE_BOUNDARY_VERSION = "0.1"


def build_bounded_executor_cycle_boundary(
    cycles_completed=0,
    ci_status="success",
    repair_attempts=0,
    human_gate_required=False,
    milestone_reached=False,
    branch="research-lab",
):
    controller = control_bounded_executor_cycle(
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
        human_gate_required=human_gate_required,
        milestone_reached=milestone_reached,
        branch=branch,
    )
    validation = validate_bounded_executor_controller_output(controller)

    plan = build_execution_cycle_plan(
        cycles_completed=cycles_completed,
        ci_status=ci_status,
        repair_attempts=repair_attempts,
    )

    boundary_open = (
        validation["valid"] is True
        and validation["ready_for_next_boundary"] is True
        and plan["plan_valid"] is True
        and plan["ready_for_execution_adapter"] is True
        and plan["human_gate_required"] is False
    )

    return {
        "version": BOUNDED_EXECUTOR_CYCLE_BOUNDARY_VERSION,
        "boundary_valid": validation["valid"] is True,
        "boundary_open": boundary_open,
        "branch": controller["branch"],
        "research_branch_only": controller["research_branch_only"],
        "cycles_completed_before": cycles_completed,
        "cycles_completed_after_plan": plan["cycles_completed"],
        "planned_steps": plan["planned_steps"] if boundary_open else (),
        "planned_step_count": len(plan["planned_steps"]) if boundary_open else 0,
        "human_gate_required": controller["human_gate_required"],
        "milestone_reached": controller["milestone_reached"],
        "reason": "bounded_cycle_boundary_ready" if boundary_open else controller["reason"],
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


def validate_bounded_executor_cycle_boundary():
    ready = build_bounded_executor_cycle_boundary(cycles_completed=0)
    assert ready["boundary_valid"] is True
    assert ready["boundary_open"] is True
    assert ready["cycles_completed_before"] == 0
    assert ready["cycles_completed_after_plan"] == 1
    assert ready["planned_step_count"] == 7
    assert ready["executor_invocation_authorized"] is False

    exhausted = build_bounded_executor_cycle_boundary(cycles_completed=10)
    assert exhausted["boundary_open"] is False
    assert exhausted["planned_steps"] == ()

    gated = build_bounded_executor_cycle_boundary(human_gate_required=True)
    assert gated["boundary_open"] is False
    assert gated["human_gate_required"] is True

    milestone = build_bounded_executor_cycle_boundary(milestone_reached=True)
    assert milestone["boundary_open"] is False

    assert build_bounded_executor_cycle_boundary(branch="main")["boundary_open"] is False
    assert build_bounded_executor_cycle_boundary(ci_status="failure")["boundary_open"] is False
    return True
