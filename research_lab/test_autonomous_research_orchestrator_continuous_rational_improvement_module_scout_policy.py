"""Tests for Module Scout reuse policy."""

from research_lab.autonomous_research_orchestrator_continuous_rational_improvement_module_scout_policy import (
    evaluate_module_candidate,
)


def run_tests():
    standard = evaluate_module_candidate({
        "source": "python_standard_library",
        "maintenance_activity": "not_applicable",
        "license_compatible": True,
        "security_reviewed": True,
        "python_compatible": True,
        "testable": True,
        "rollback_easy": True,
        "custom_code_reduction": 120,
        "dependency_weight": "none",
    })
    assert standard["allowed_for_experiment"] is True
    assert standard["source_priority"] == 5
    assert standard["requires_human_gate_for_external_install"] is False
    assert standard["auto_install_authorized"] is False
    assert standard["external_action_authorized"] is False

    plugin = evaluate_module_candidate({
        "source": "chatgpt_plugin",
        "maintenance_activity": "high",
        "license_compatible": True,
        "security_reviewed": True,
        "python_compatible": True,
        "testable": True,
        "rollback_easy": True,
        "custom_code_reduction": 40,
        "dependency_weight": "low",
    })
    assert plugin["allowed_for_experiment"] is True
    assert plugin["requires_human_gate_for_external_install"] is True
    assert plugin["network_execution_authorized"] is False

    unsafe = evaluate_module_candidate({
        "source": "mature_open_source_module",
        "maintenance_activity": "high",
        "license_compatible": True,
        "security_reviewed": False,
        "python_compatible": True,
        "testable": True,
        "rollback_easy": True,
        "custom_code_reduction": 80,
        "dependency_weight": "low",
    })
    assert unsafe["allowed_for_experiment"] is False

    heavy = evaluate_module_candidate({
        "source": "official_api_or_sdk",
        "maintenance_activity": "high",
        "license_compatible": True,
        "security_reviewed": True,
        "python_compatible": True,
        "testable": True,
        "rollback_easy": True,
        "custom_code_reduction": 80,
        "dependency_weight": "high",
    })
    assert heavy["allowed_for_experiment"] is False

    assert evaluate_module_candidate(None)["allowed_for_experiment"] is False
    assert evaluate_module_candidate({"source": "unknown"})["allowed_for_experiment"] is False


if __name__ == "__main__":
    run_tests()
    print("module scout policy tests passed")
