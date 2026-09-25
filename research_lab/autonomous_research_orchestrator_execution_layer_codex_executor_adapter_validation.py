"""Validate Codex executor adapter design snapshots independently and fail closed."""

from collections.abc import Mapping

CODEX_EXECUTOR_ADAPTER_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "adapter_valid",
    "adapter_ready",
    "provider",
    "mode",
    "branch",
    "request_steps",
    "request_count",
    "requires_future_activation_review",
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


def validate_codex_executor_adapter_output(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    ready = snapshot.get("adapter_ready") is True

    if snapshot.get("provider") != "codex":
        errors.append("invalid_provider")
    if snapshot.get("mode") != "design_only":
        errors.append("invalid_mode")

    branch = snapshot.get("branch")
    if ready and branch != "research-lab":
        errors.append("ready_outside_research_branch")
    if not ready and branch is not None:
        errors.append("blocked_adapter_has_branch")

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
        if snapshot.get("adapter_valid") is not True:
            errors.append("ready_invalid_adapter")
        if count != 7:
            errors.append("ready_without_full_canonical_request_set")
        if not all(isinstance(step, str) and step for step in steps):
            errors.append("invalid_request_step")
        if snapshot.get("requires_future_activation_review") is not True:
            errors.append("ready_without_future_activation_review")
    else:
        if steps != ():
            errors.append("blocked_adapter_has_requests")
        if snapshot.get("requires_future_activation_review") is not False:
            errors.append("blocked_adapter_activation_review_flag")

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
        "version": CODEX_EXECUTOR_ADAPTER_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_codex_activation_boundary": valid and ready,
        "errors": tuple(errors),
        "codex_invocation_authorized": False,
        "external_action_authorized": False,
    }
