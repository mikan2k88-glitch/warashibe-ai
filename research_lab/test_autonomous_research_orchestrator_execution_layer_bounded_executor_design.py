"""Tests for bounded executor design."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_design import (
    bounded_executor_design,
    validate_bounded_executor_design,
)


def run_tests():
    assert validate_bounded_executor_design() is True

    design = bounded_executor_design()
    assert design["design_valid"] is True
    assert design["research_branch_only"] is True
    assert design["max_autonomous_cycles"] == 10
    assert design["one_theme_per_cycle"] is True
    assert design["requires_green_ci"] is True
    assert design["max_repair_attempts_per_cycle"] == 1
    assert design["stop_on_human_gate"] is True
    assert design["stop_on_unknown_action"] is True
    assert design["stop_at_milestone"] is True
    assert design["executor_invocation_authorized"] is False
    assert design["executor_invoked"] is False
    assert design["external_action_authorized"] is False

    assert bounded_executor_design(branch="main")["design_valid"] is False
    assert bounded_executor_design(max_cycles=0)["design_valid"] is False
    assert bounded_executor_design(max_cycles=11)["design_valid"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor design tests passed")
