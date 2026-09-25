"""Tests for bounded Codex milestone executor design."""

from research_lab.codex_milestone_executor_design import (
    REQUIRED_COMPLETION_CHECKS,
    build_codex_milestone_contract,
    evaluate_milestone_completion,
    validate_codex_milestone_contract,
)


def run_tests():
    assert validate_codex_milestone_contract() is True

    contract = build_codex_milestone_contract()
    assert contract["executor"] == "codex"
    assert contract["allowed_branches"] == ("research-lab", "main")
    assert contract["execution_limits"]["max_cycles"] == 10
    assert contract["execution_limits"]["max_repairs_per_cycle"] == 1
    assert contract["execution_limits"]["require_ci_green_before_next_cycle"] is True
    assert contract["execution_limits"]["stop_on_human_gate"] is True
    assert contract["codex_invocation_authorized"] is False
    assert contract["main_code_changes_allowed"] is True
    assert contract["main_branch_write_requires_human_gate"] is True
    assert contract["main_branch_change_authorized"] is False
    assert contract["commerce_authorized"] is False

    complete_state = {check: True for check in REQUIRED_COMPLETION_CHECKS}
    complete = evaluate_milestone_completion(complete_state)
    assert complete["complete"] is True
    assert complete["missing"] == ()
    assert complete["codex_should_stop"] is True
    assert complete["requires_human_review_before_external_activation"] is True

    incomplete_state = {check: True for check in REQUIRED_COMPLETION_CHECKS}
    incomplete_state["latest_ci_green"] = False
    incomplete = evaluate_milestone_completion(incomplete_state)
    assert incomplete["complete"] is False
    assert incomplete["missing"] == ("latest_ci_green",)
    assert incomplete["codex_should_stop"] is False


if __name__ == "__main__":
    run_tests()
    print("Codex milestone executor design tests passed")
