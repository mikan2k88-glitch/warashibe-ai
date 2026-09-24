"""Validate bounded executor handoff boundary output independently and fail closed."""

from collections.abc import Mapping

BOUNDED_EXECUTOR_HANDOFF_BOUNDARY_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "handoff_valid",
    "handoff_ready",
    "branch",
    "research_branch_only",
    "cycles_completed_before",
    "cycles_completed_after_plan",
    "requests",
    "request_count",
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


def validate_bounded_executor_handoff_boundary_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    ready = snapshot.get("handoff_ready") is True
    valid_handoff = snapshot.get("handoff_valid") is True

    if ready and not valid_handoff:
        errors.append("ready_invalid_handoff")
    if ready and snapshot.get("branch") != "research-lab":
        errors.append("ready_outside_research_branch")
    if ready and snapshot.get("research_branch_only") is not True:
        errors.append("ready_without_research_branch_only")

    before = snapshot.get("cycles_completed_before")
    after = snapshot.get("cycles_completed_after_plan")
    if not isinstance(before, int) or isinstance(before, bool) or not 0 <= before <= 10:
        errors.append("invalid_cycles_before")
    if not isinstance(after, int) or isinstance(after, bool) or not 0 <= after <= 10:
        errors.append("invalid_cycles_after")
    if ready and after != before + 1:
        errors.append("ready_cycle_increment_not_one")
    if before == 10 and ready:
        errors.append("ready_after_cycle_budget_exhausted")

    requests = snapshot.get("requests")
    request_count = snapshot.get("request_count")
    if not isinstance(requests, tuple):
        errors.append("requests_not_tuple")
        requests = ()
    if not isinstance(request_count, int) or isinstance(request_count, bool):
        errors.append("invalid_request_count")
    elif request_count != len(requests):
        errors.append("request_count_mismatch")

    request_shape_valid = all(
        isinstance(request, dict)
        and isinstance(request.get("step"), str)
        and request.get("requested") is True
        and request.get("performed") is False
        and request.get("external_action_authorized") is False
        for request in requests
    )
    if not request_shape_valid:
        errors.append("invalid_request_shape")
    if ready and request_count != 7:
        errors.append("ready_without_full_canonical_request_set")
    if not ready and requests != ():
        errors.append("blocked_handoff_has_requests")

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
        "version": BOUNDED_EXECUTOR_HANDOFF_BOUNDARY_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_executor_adapter": valid and ready,
        "errors": tuple(errors),
        "external_action_authorized": False,
    }
