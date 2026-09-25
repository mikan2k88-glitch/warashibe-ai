"""Tests for continuous rational-improvement Kaizen loop design."""

from research_lab.autonomous_research_orchestrator_continuous_rational_improvement_kaizen_loop_design import (
    build_kaizen_loop_design,
    validate_kaizen_loop_design,
)


def run_tests():
    assert validate_kaizen_loop_design() is True

    design = build_kaizen_loop_design()
    assert design["module_scout_enabled"] is True
    assert design["prefer_reuse_before_build"] is True
    assert design["requires_small_reversible_experiment"] is True
    assert design["requires_ci_comparison"] is True
    assert design["auto_large_refactor"] is False
    assert design["auto_external_install"] is False
    assert design["external_action_authorized"] is False
    assert design["improvement_flow"][0] == "review_existing_system"
    assert design["improvement_flow"][-1] == "standardize_if_adopted"


if __name__ == "__main__":
    run_tests()
    print("kaizen loop design tests passed")
