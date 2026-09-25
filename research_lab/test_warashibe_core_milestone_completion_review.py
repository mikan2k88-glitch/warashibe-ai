"""Tests for milestone completion review."""

from research_lab.warashibe_core_milestone_completion_review import (
    review_milestone_completion,
)


def run_tests():
    result = review_milestone_completion()

    assert result["completed"] is True
    assert result["completion_state"] == "milestone_complete"
    assert result["next_milestone"] == "sandbox_external_integration"
    assert result["blockers"] == ()
    assert result["main_merge_authorized"] is False
    assert result["production_rollout_authorized"] is False
    assert result["external_execution_authorized"] is False
    assert result["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("warashibe core milestone completion review tests passed")
