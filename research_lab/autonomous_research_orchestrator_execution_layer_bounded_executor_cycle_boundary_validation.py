"""Validate bounded executor cycle boundary output independently and fail closed."""

from collections.abc import Mapping

BOUNDED_EXECUTOR_CYCLE_BOUNDARY_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "boundary_valid",
    "boundary_open",
    "branch",
    "research_branch_only",
    "cycles_completed_before",
    "cycles_completed_after_plan",
    "planned_steps",
    "planned_step_count",
    "human_gate_required",
    "milestone_reached",
    "reason",
    "executor_invocation_authorized",
    "executor_invoked",
    "main_branch_authorized",
    "credentials_change_authorized",
    "production_change_authorized",
    "commerce_authorized",
    "notification_authorized",
    "external_action_authorized",
    "external_action_performed",
)


def validate_bounded_executor_cycle_boundary_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    open_ = snapshot.get("boundary_open") is True
    valid_boundary = snapshot.get("boundary_valid") is True

    if open_ and not valid_boundary:
        errors.append("open_invalid_boundary")
    if open_ and snapshot.get("branch") != "research-lab":
        errors.append("open_outside_research_branch")
    if open_ and snapshot.get("research_branch_only") is not True:
        errors.append("open_without_research_branch_only")
    if open_ and snapshot.get("human_gate_required") is not False:
        errors.append("open_with_human_gate")
    if open_ and snapshot.get("milestone_reached") is not False:
        errors.append("open_after_milestone")

    before = snapshot.get("cycles_completed_before")
    after = snapshot.get("cycles_completed_after_plan")
    if not isinstance(before, int) or isinstance(before, bool) or not 0 <= before <= 10:
        errors.append("invalid_cycles_before")
    if not isinstance(after, int) or isinstance(after, bool) or not 0 <= after <= 10:
        errors.append("invalid_cycles_after")
    if open_ and after != before + 1:
        errors.append("open_cycle_increment_not_one")
    if before == 10 and open_:
        errors.append("open_after_cycle_budget_exhausted")

    planned_steps = snapshot.get("planned_steps")
    planned_count = snapshot.get("planned_step_count")
    if not isinstance(planned_steps, tuple):
        errors.append("planned_steps_not_tuple")
        planned_steps = ()
    if not isinstance(planned_count, int) or isinstance(planned_count, bool):
        errors.append("invalid_planned_step_count")
    elif planned_count != len(planned_steps):
        errors.append("planned_step_count_mismatch")
    if open_ and planned_count != 7:
        errors.append("open_without_full_canonical_plan")
    if not open_ and planned_steps != ():
        errors.append("closed_boundary_has_planned_steps")

    for field in (
        "executor_invocation_authorized",
        "executor_invoked",
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "notification_authorized",
        "external_action_authorized",
        "external_action_performed",
    ):
        if snapshot.get(field) is not False:
            errors.append(f"unsafe_{field}")

    valid = not errors
    return {
        "version": BOUNDED_EXECUTOR_CYCLE_BOUNDARY_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_executor_handoff_boundary": valid and open_,
        "errors": tuple(errors),
        "external_action_authorized": False,
    }
