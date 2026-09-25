"""Validate Module Scout policy decisions independently and fail closed."""

from collections.abc import Mapping

MODULE_SCOUT_VALIDATION_VERSION = "0.1"

_REQUIRED_FIELDS = (
    "allowed_for_experiment",
    "source",
    "source_priority",
    "reason",
    "requires_research_lab_only",
    "requires_ci_comparison",
    "requires_human_gate_for_external_install",
    "auto_install_authorized",
    "auto_dependency_upgrade_authorized",
    "network_execution_authorized",
    "main_branch_authorized",
    "production_change_authorized",
    "external_action_authorized",
)


def validate_module_scout_decision(snapshot):
    errors = []

    if not isinstance(snapshot, Mapping):
        errors.append("snapshot_not_mapping")
        snapshot = {}

    for field in _REQUIRED_FIELDS:
        if field not in snapshot:
            errors.append(f"missing_{field}")

    allowed = snapshot.get("allowed_for_experiment") is True
    source = snapshot.get("source")
    priority = snapshot.get("source_priority")

    if not isinstance(priority, int) or isinstance(priority, bool) or not 0 <= priority <= 5:
        errors.append("invalid_source_priority")

    if snapshot.get("requires_research_lab_only") is not True:
        errors.append("research_lab_requirement_missing")
    if snapshot.get("requires_ci_comparison") is not True:
        errors.append("ci_comparison_requirement_missing")

    if allowed:
        if source not in (
            "python_standard_library",
            "official_api_or_sdk",
            "chatgpt_plugin",
            "mature_open_source_module",
            "internal_shared_module",
        ):
            errors.append("allowed_unknown_source")
        if not isinstance(snapshot.get("reason"), str) or not snapshot.get("reason"):
            errors.append("allowed_without_reason")
        if source == "python_standard_library":
            if snapshot.get("requires_human_gate_for_external_install") is not False:
                errors.append("stdlib_external_install_gate_invalid")
        elif snapshot.get("requires_human_gate_for_external_install") is not True:
            errors.append("external_source_without_install_gate")

    for field in (
        "auto_install_authorized",
        "auto_dependency_upgrade_authorized",
        "network_execution_authorized",
        "main_branch_authorized",
        "production_change_authorized",
        "external_action_authorized",
    ):
        if snapshot.get(field) is not False:
            errors.append(f"unsafe_{field}")

    valid = not errors
    return {
        "version": MODULE_SCOUT_VALIDATION_VERSION,
        "valid": valid,
        "ready_for_small_reversible_experiment": valid and allowed,
        "errors": tuple(errors),
        "external_action_authorized": False,
    }
