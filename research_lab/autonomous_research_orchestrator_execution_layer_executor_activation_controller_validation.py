"""Validate executor activation controller output independently and fail closed."""

from collections.abc import Mapping

EXECUTOR_ACTIVATION_CONTROLLER_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "state",
    "executor_ready",
    "reason",
    "branch",
    "max_autonomous_cycles",
    "cycles_completed",
    "milestone_bounded",
    "research_branch_only",
    "requires_green_ci",
    "human_gate_approved",
    "executor_invoked",
    "main_branch_authorized",
    "credentials_change_authorized",
    "production_change_authorized",
    "commerce_authorized",
    "notification_authorized",
)


def validate_executor_activation_controller_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    ready = snapshot.get("executor_ready") is True
    state = snapshot.get("state")

    if state not in ("ready", "stopped"):
        errors.append("invalid_state")
    if ready != (state == "ready"):
        errors.append("state_ready_mismatch")
    if ready and snapshot.get("branch") != "research-lab":
        errors.append("ready_outside_research_branch")
    if ready and snapshot.get("human_gate_approved") is not True:
        errors.append("ready_without_human_gate")
    if ready and snapshot.get("cycles_completed") != 0:
        errors.append("ready_cycle_count_not_zero")
    if snapshot.get("executor_invoked") is not False:
        errors.append("executor_already_invoked")

    max_cycles = snapshot.get("max_autonomous_cycles")
    if not isinstance(max_cycles, int) or isinstance(max_cycles, bool) or not 1 <= max_cycles <= 10:
        errors.append("invalid_cycle_budget")

    for field in (
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
    ):
        if snapshot.get(field) is not False:
            errors.append(f"unsafe_{field}")

    valid = not errors
    return {
        "version": EXECUTOR_ACTIVATION_CONTROLLER_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_executor_boundary": valid and ready,
        "errors": tuple(errors),
        "external_action_authorized": False,
    }


def validate_executor_activation_readiness():
    """Compose activation and repaired cycle-accounting checks locally."""
    from research_lab.autonomous_research_orchestrator_execution_layer_cycle_accounting_validation import (
        validate_cycle_accounting,
    )
    from research_lab.autonomous_research_orchestrator_execution_layer_executor_activation_controller import (
        control_executor_activation,
    )

    activation = control_executor_activation(human_gate_approved=True)
    activation_validation = validate_executor_activation_controller_output(activation)
    first_cycle = validate_cycle_accounting(0)
    last_cycle = validate_cycle_accounting(9)
    exhausted = validate_cycle_accounting(10)

    ready = (
        activation_validation["valid"] is True
        and activation_validation["ready_for_executor_boundary"] is True
        and first_cycle["valid"] is True
        and first_cycle["cycles_after"] == 1
        and last_cycle["valid"] is True
        and last_cycle["cycles_after"] == 10
        and exhausted["valid"] is False
        and exhausted["cycles_after"] == 10
        and activation["executor_invoked"] is False
    )
    return {
        "version": EXECUTOR_ACTIVATION_CONTROLLER_VALIDATION_VERSION,
        "valid": ready,
        "ready_for_bounded_executor": ready,
        "cycle_budget_limit": activation["max_autonomous_cycles"],
        "first_cycle_after": first_cycle["cycles_after"],
        "last_cycle_after": last_cycle["cycles_after"],
        "exhausted_cycle_after": exhausted["cycles_after"],
        "external_action_authorized": False,
    }
