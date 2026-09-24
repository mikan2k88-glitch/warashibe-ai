"""Validate bounded executor controller output independently and fail closed."""

from collections.abc import Mapping

BOUNDED_EXECUTOR_CONTROLLER_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "state",
    "cycle_ready",
    "continue_autonomous_research",
    "reason",
    "branch",
    "research_branch_only",
    "cycles_completed",
    "max_autonomous_cycles",
    "repair_attempts",
    "max_repair_attempts_per_cycle",
    "requires_green_ci",
    "human_gate_required",
    "milestone_reached",
    "executor_invocation_authorized",
    "executor_invoked",
    "main_branch_authorized",
    "credentials_change_authorized",
    "production_change_authorized",
    "commerce_authorized",
    "notification_authorized",
    "external_action_authorized",
)


def validate_bounded_executor_controller_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    ready = snapshot.get("cycle_ready") is True
    state = snapshot.get("state")

    if state not in ("ready", "stopped"):
        errors.append("invalid_state")
    if ready != (state == "ready"):
        errors.append("state_ready_mismatch")
    if snapshot.get("continue_autonomous_research") is not ready:
        errors.append("continue_ready_mismatch")
    if ready and snapshot.get("branch") != "research-lab":
        errors.append("ready_outside_research_branch")
    if ready and snapshot.get("research_branch_only") is not True:
        errors.append("ready_without_research_branch_only")
    if ready and snapshot.get("human_gate_required") is not False:
        errors.append("ready_with_human_gate")
    if ready and snapshot.get("milestone_reached") is not False:
        errors.append("ready_after_milestone")

    cycles = snapshot.get("cycles_completed")
    if not isinstance(cycles, int) or isinstance(cycles, bool) or not 0 <= cycles <= 10:
        errors.append("invalid_cycles_completed")

    repairs = snapshot.get("repair_attempts")
    if not isinstance(repairs, int) or isinstance(repairs, bool) or not 0 <= repairs <= 1:
        errors.append("invalid_repair_attempts")

    if snapshot.get("max_autonomous_cycles") != 10:
        errors.append("invalid_cycle_budget")
    if snapshot.get("max_repair_attempts_per_cycle") != 1:
        errors.append("invalid_repair_budget")
    if snapshot.get("requires_green_ci") is not True:
        errors.append("green_ci_not_required")

    for field in (
        "executor_invocation_authorized",
        "executor_invoked",
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
        "external_action_authorized",
    ):
        if snapshot.get(field) is not False:
            errors.append(f"unsafe_{field}")

    valid = not errors
    return {
        "version": BOUNDED_EXECUTOR_CONTROLLER_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_next_boundary": valid and ready,
        "errors": tuple(errors),
        "external_action_authorized": False,
    }
