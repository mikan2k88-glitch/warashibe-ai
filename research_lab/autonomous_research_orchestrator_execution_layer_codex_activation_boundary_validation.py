"""Validate Codex activation-boundary snapshots independently and fail closed."""

from collections.abc import Mapping

CODEX_ACTIVATION_BOUNDARY_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "boundary_valid",
    "boundary_ready",
    "provider",
    "branch",
    "request_steps",
    "request_count",
    "human_gate_required_for_activation",
    "activation_review_only",
    "codex_invocation_authorized",
    "codex_invoked",
    "network_access_authorized",
    "main_branch_authorized",
    "credentials_change_authorized",
    "production_change_authorized",
    "commerce_authorized",
    "external_action_authorized",
    "external_action_performed",
)


def validate_codex_activation_boundary_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    ready = snapshot.get("boundary_ready") is True

    if snapshot.get("provider") != "codex":
        errors.append("invalid_provider")
    if snapshot.get("activation_review_only") is not True:
        errors.append("activation_not_review_only")

    branch = snapshot.get("branch")
    if ready and branch != "research-lab":
        errors.append("ready_outside_research_branch")
    if not ready and branch is not None:
        errors.append("blocked_boundary_has_branch")

    steps = snapshot.get("request_steps")
    count = snapshot.get("request_count")
    if not isinstance(steps, tuple):
        errors.append("request_steps_not_tuple")
        steps = ()
    if not isinstance(count, int) or isinstance(count, bool):
        errors.append("invalid_request_count")
    elif count != len(steps):
        errors.append("request_count_mismatch")

    if ready:
        if snapshot.get("boundary_valid") is not True:
            errors.append("ready_invalid_boundary")
        if count != 7:
            errors.append("ready_without_full_canonical_request_set")
        if snapshot.get("human_gate_required_for_activation") is not True:
            errors.append("ready_without_human_gate")
    else:
        if steps != ():
            errors.append("blocked_boundary_has_requests")
        if snapshot.get("human_gate_required_for_activation") is not False:
            errors.append("blocked_boundary_human_gate_flag")

    for field in (
        "codex_invocation_authorized",
        "codex_invoked",
        "network_access_authorized",
        "main_branch_authorized",
        "credentials_change_authorized",
        "production_change_authorized",
        "commerce_authorized",
        "external_action_authorized",
        "external_action_performed",
    ):
        if snapshot.get(field) is not False:
            errors.append(f"unsafe_{field}")

    valid = not errors
    return {
        "version": CODEX_ACTIVATION_BOUNDARY_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_codex_activation_review": valid and ready,
        "human_gate_required": valid and ready,
        "errors": tuple(errors),
        "codex_invocation_authorized": False,
        "external_action_authorized": False,
    }
