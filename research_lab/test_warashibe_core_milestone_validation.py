"""Tests for Warashibe AI real-world milestone validation."""

from research_lab.warashibe_core_milestone_validation import (
    validate_real_world_core_milestone,
)


def run_tests():
    result = validate_real_world_core_milestone()

    assert result["passed"] is True
    assert result["milestone"] == "real_world_core_to_human_gate"
    assert result["terminal_status"] == "ready_for_human_gate"
    assert result["checks"]["boundary_passed"] is True
    assert result["checks"]["policy_passed"] is True
    assert result["checks"]["scoring_passed"] is True
    assert result["checks"]["single_candidate_selected"] is True
    assert result["checks"]["route_present"] is True
    assert result["checks"]["network_disabled"] is True
    assert result["checks"]["purchase_disabled"] is True
    assert result["checks"]["payment_disabled"] is True
    assert result["checks"]["external_action_disabled"] is True
    assert result["execution_authorized"] is False
    assert result["commerce_authorized"] is False
    assert result["main_branch_change_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("warashibe core milestone validation tests passed")
