"""Tests for independent Module Scout validation."""

from research_lab.autonomous_research_orchestrator_continuous_rational_improvement_module_scout_policy import (
    evaluate_module_candidate,
)
from research_lab.autonomous_research_orchestrator_continuous_rational_improvement_module_scout_validation import (
    validate_module_scout_decision,
)


def _candidate(source="python_standard_library"):
    return {
        "source": source,
        "maintenance_activity": "not_applicable" if source == "python_standard_library" else "high",
        "license_compatible": True,
        "security_reviewed": True,
        "python_compatible": True,
        "testable": True,
        "rollback_easy": True,
        "custom_code_reduction": 50,
        "dependency_weight": "none" if source == "python_standard_library" else "low",
    }


def run_tests():
    stdlib = validate_module_scout_decision(
        evaluate_module_candidate(_candidate("python_standard_library"))
    )
    assert stdlib["valid"] is True
    assert stdlib["ready_for_small_reversible_experiment"] is True
    assert stdlib["external_action_authorized"] is False

    plugin = validate_module_scout_decision(
        evaluate_module_candidate(_candidate("chatgpt_plugin"))
    )
    assert plugin["valid"] is True
    assert plugin["ready_for_small_reversible_experiment"] is True

    blocked = evaluate_module_candidate({
        **_candidate("mature_open_source_module"),
        "security_reviewed": False,
    })
    result = validate_module_scout_decision(blocked)
    assert result["valid"] is True
    assert result["ready_for_small_reversible_experiment"] is False

    tampered = dict(evaluate_module_candidate(_candidate("official_api_or_sdk")))
    tampered["auto_install_authorized"] = True
    assert validate_module_scout_decision(tampered)["valid"] is False

    tampered = dict(evaluate_module_candidate(_candidate("chatgpt_plugin")))
    tampered["requires_human_gate_for_external_install"] = False
    assert validate_module_scout_decision(tampered)["valid"] is False

    tampered = dict(evaluate_module_candidate(_candidate("python_standard_library")))
    tampered["requires_research_lab_only"] = False
    assert validate_module_scout_decision(tampered)["valid"] is False

    # Reject every attempted permission escalation independently.
    baseline = evaluate_module_candidate(_candidate("official_api_or_sdk"))
    for field in (
        "auto_install_authorized",
        "auto_dependency_upgrade_authorized",
        "network_execution_authorized",
        "main_branch_authorized",
        "production_change_authorized",
        "external_action_authorized",
    ):
        changed = dict(baseline)
        changed[field] = True
        outcome = validate_module_scout_decision(changed)
        assert outcome["valid"] is False, field
        assert outcome["external_action_authorized"] is False

    # Missing required decisions and malformed priority fail closed.
    # Version is metadata in the current v0.1 validator, not a required decision field.
    # Assert the actual required contract rather than imposing a new rule in a test.
    for field in (
        "allowed_for_experiment", "source", "source_priority", "reason",
        "requires_research_lab_only", "requires_ci_comparison",
        "requires_human_gate_for_external_install", "auto_install_authorized",
        "auto_dependency_upgrade_authorized", "network_execution_authorized",
        "main_branch_authorized", "production_change_authorized",
        "external_action_authorized",
    ):
        changed = dict(baseline)
        del changed[field]
        assert validate_module_scout_decision(changed)["valid"] is False, field
    for priority in (True, -1, 6, "5", 2.5, None):
        changed = dict(baseline)
        changed["source_priority"] = priority
        assert validate_module_scout_decision(changed)["valid"] is False

    for source in (
        "official_api_or_sdk", "chatgpt_plugin",
        "mature_open_source_module", "internal_shared_module",
    ):
        result = validate_module_scout_decision(evaluate_module_candidate(_candidate(source)))
        assert result["valid"] is True
        assert result["ready_for_small_reversible_experiment"] is True
        assert result["external_action_authorized"] is False

    assert validate_module_scout_decision(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("module scout validation tests passed")
