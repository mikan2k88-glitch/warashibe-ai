"""Tests for autonomous research controller-policy guard."""

from research_lab.autonomous_research_controller_policy_guard import (
    guard_planning_request,
    validate_controller_policy_guard,
)


def run_tests():
    assert validate_controller_policy_guard() is True

    proceed = guard_planning_request("proceed", "prepare_research_change")
    assert proceed["policy_allowed"] is True
    assert proceed["within_budget"] is True
    assert proceed["limit"] == 1
    assert proceed["external_action_authorized"] is False

    exhausted = guard_planning_request("repair", "prepare_repair", 1)
    assert exhausted["policy_allowed"] is True
    assert exhausted["within_budget"] is False
    assert exhausted["allowed"] is False
    assert exhausted["external_action_performed"] is False

    for invalid in (-1, True, 1.5):
        try:
            guard_planning_request("proceed", "prepare_research_change", invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid usage count must be rejected")


if __name__ == "__main__":
    run_tests()
    print("autonomous research controller policy guard tests passed")
