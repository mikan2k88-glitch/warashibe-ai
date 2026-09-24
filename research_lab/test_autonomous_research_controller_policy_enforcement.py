"""Tests for autonomous research controller-policy enforcement."""

from research_lab.autonomous_research_controller_policy_enforcement import (
    enforce_planning_operation,
    validate_controller_policy_enforcement,
)


def run_tests():
    assert validate_controller_policy_enforcement() is True

    allowed = enforce_planning_operation("proceed", "prepare_research_change")
    assert allowed["allowed"] is True
    assert allowed["effective_limits"]["themes_per_cycle"] == 1
    assert allowed["external_action_authorized"] is False

    denied = enforce_planning_operation("stop", "prepare_research_change")
    assert denied["allowed"] is False
    assert denied["reason"] == "denied_by_controller_policy"
    assert "modify_main_branch" in denied["forbidden_actions"]
    assert denied["credentials_included"] is False

    try:
        enforce_planning_operation("proceed", "unknown")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown planning operation must be rejected")


if __name__ == "__main__":
    run_tests()
    print("autonomous research controller policy enforcement tests passed")
