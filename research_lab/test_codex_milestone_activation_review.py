"""Tests for Codex milestone activation review."""

from research_lab.codex_milestone_activation_review import (
    run_codex_milestone_activation_review,
    validate_codex_milestone_activation_review,
)


def run_tests():
    assert validate_codex_milestone_activation_review() is True

    review = run_codex_milestone_activation_review()
    assert review["ready_for_human_gate"] is True
    assert review["blockers"] == ()
    assert review["next_required_action"] == (
        "request_explicit_codex_invocation_approval"
    )
    assert review["codex_invocation_authorized"] is False
    assert review["network_execution_authorized"] is False
    assert review["secret_access_authorized"] is False
    assert review["commerce_authorized"] is False
    assert review["production_change_authorized"] is False
    assert review["main_branch_change_authorized"] is False
    assert review["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex milestone activation review tests passed")
