"""Tests for autonomous research controller-policy bridge."""

from research_lab.autonomous_research_controller_policy_bridge import (
    controller_policy_bridge,
    validate_controller_policy_bridge,
)


def run_tests():
    assert validate_controller_policy_bridge() is True

    repair = controller_policy_bridge("repair")
    assert repair["may_prepare_repair"] is True
    assert repair["may_prepare_research_change"] is False
    assert repair["effective_limits"]["code_changes_per_cycle"] == 3

    wait = controller_policy_bridge("wait")
    assert wait["must_wait"] is True
    assert wait["external_action_performed"] is False

    stop = controller_policy_bridge("stop")
    assert stop["must_stop"] is True
    assert "modify_main_branch" in stop["forbidden_actions"]
    assert stop["credentials_included"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research controller policy bridge tests passed")
