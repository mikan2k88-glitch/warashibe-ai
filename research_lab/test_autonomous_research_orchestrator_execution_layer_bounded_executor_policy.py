"""Tests for bounded executor cycle policy."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_policy import (
    evaluate_bounded_executor_cycle,
    validate_bounded_executor_policy,
)


def run_tests():
    assert validate_bounded_executor_policy() is True

    allowed = evaluate_bounded_executor_cycle(cycles_completed=9, repair_attempts=1)
    assert allowed["allowed"] is True
    assert allowed["stop_required"] is False
    assert allowed["research_branch_only"] is True
    assert allowed["max_autonomous_cycles"] == 10
    assert allowed["max_repair_attempts_per_cycle"] == 1
    assert allowed["executor_invocation_authorized"] is False
    assert allowed["external_action_authorized"] is False

    exhausted = evaluate_bounded_executor_cycle(cycles_completed=10)
    assert exhausted["allowed"] is False
    assert exhausted["reason"] == "cycle_budget_invalid_or_exhausted"

    gated = evaluate_bounded_executor_cycle(human_gate_required=True)
    assert gated["allowed"] is False
    assert gated["reason"] == "human_gate_required"

    milestone = evaluate_bounded_executor_cycle(milestone_reached=True)
    assert milestone["allowed"] is False
    assert milestone["reason"] == "milestone_reached"

    assert evaluate_bounded_executor_cycle(branch="main")["allowed"] is False
    assert evaluate_bounded_executor_cycle(cycles_completed=True)["allowed"] is False
    assert evaluate_bounded_executor_cycle(repair_attempts=True)["allowed"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor policy tests passed")
