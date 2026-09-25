"""Tests for sandbox experiment environment design."""

from research_lab.autonomous_research_orchestrator_sandbox_experiment_environment_design import (
    build_sandbox_experiment_environment_design,
    validate_sandbox_experiment_environment_design,
)


def run_tests():
    assert validate_sandbox_experiment_environment_design() is True

    design = build_sandbox_experiment_environment_design()
    assert design["disposable"] is True
    assert design["research_lab_only"] is True
    assert design["resource_limits"]["cpu_seconds"] > 0
    assert design["resource_limits"]["memory_mb"] > 0
    assert design["network_policy"]["enabled"] is False
    assert design["secret_policy"]["inject_secrets"] is False
    assert design["filesystem_policy"]["project_mount"] == "read_only"
    assert design["filesystem_policy"]["persist_artifacts"] is False
    assert design["execution_authorized"] is False
    assert design["external_action_authorized"] is False
    assert "module_scout_experiment" in design["allowed_purposes"]
    assert "real_world_market_adapter_dry_run" in design["allowed_purposes"]


if __name__ == "__main__":
    run_tests()
    print("sandbox experiment environment design tests passed")
