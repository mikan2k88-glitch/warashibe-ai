"""Policy for evaluating reusable modules before writing new custom code.

This policy is pure and fail-closed. It ranks a supplied candidate using
explicit evidence only; it does not search the web, install packages, connect
plugins, or authorize external actions.
"""

MODULE_SCOUT_POLICY_VERSION = "0.1"

ALLOWED_SOURCES = (
    "python_standard_library",
    "official_api_or_sdk",
    "chatgpt_plugin",
    "mature_open_source_module",
    "internal_shared_module",
)

SOURCE_PRIORITY = {
    "python_standard_library": 5,
    "official_api_or_sdk": 4,
    "internal_shared_module": 3,
    "mature_open_source_module": 2,
    "chatgpt_plugin": 2,
}

REQUIRED_EVIDENCE_FIELDS = (
    "maintenance_activity",
    "license_compatible",
    "security_reviewed",
    "python_compatible",
    "testable",
    "rollback_easy",
    "custom_code_reduction",
)


def evaluate_module_candidate(candidate):
    if not isinstance(candidate, dict):
        return _reject("candidate_not_mapping")

    source = candidate.get("source")
    if source not in ALLOWED_SOURCES:
        return _reject("unsupported_source", source=source)

    for field in REQUIRED_EVIDENCE_FIELDS:
        if field not in candidate:
            return _reject(f"missing_{field}", source=source)

    boolean_fields = (
        "license_compatible",
        "security_reviewed",
        "python_compatible",
        "testable",
        "rollback_easy",
    )
    if any(candidate.get(field) is not True for field in boolean_fields):
        return _reject("required_safety_or_compatibility_check_failed", source=source)

    maintenance = candidate.get("maintenance_activity")
    reduction = candidate.get("custom_code_reduction")
    dependency_weight = candidate.get("dependency_weight", "unknown")

    if maintenance not in ("high", "medium", "not_applicable"):
        return _reject("maintenance_evidence_insufficient", source=source)
    if not isinstance(reduction, (int, float)) or isinstance(reduction, bool) or reduction < 0:
        return _reject("invalid_custom_code_reduction", source=source)
    if dependency_weight not in ("none", "low", "medium", "high", "unknown"):
        return _reject("invalid_dependency_weight", source=source)
    if dependency_weight == "high":
        return _reject("dependency_weight_too_high", source=source)

    experiment_worthy = reduction > 0
    reason = "small_reversible_experiment_allowed" if experiment_worthy else "no_clear_reuse_benefit"

    return {
        "version": MODULE_SCOUT_POLICY_VERSION,
        "allowed_for_experiment": experiment_worthy,
        "source": source,
        "source_priority": SOURCE_PRIORITY[source],
        "reason": reason,
        "requires_research_lab_only": True,
        "requires_ci_comparison": True,
        "requires_human_gate_for_external_install": source != "python_standard_library",
        "auto_install_authorized": False,
        "auto_dependency_upgrade_authorized": False,
        "network_execution_authorized": False,
        "main_branch_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
    }


def _reject(reason, source=None):
    return {
        "version": MODULE_SCOUT_POLICY_VERSION,
        "allowed_for_experiment": False,
        "source": source,
        "source_priority": SOURCE_PRIORITY.get(source, 0),
        "reason": reason,
        "requires_research_lab_only": True,
        "requires_ci_comparison": True,
        "requires_human_gate_for_external_install": source not in (None, "python_standard_library"),
        "auto_install_authorized": False,
        "auto_dependency_upgrade_authorized": False,
        "network_execution_authorized": False,
        "main_branch_authorized": False,
        "production_change_authorized": False,
        "external_action_authorized": False,
    }
