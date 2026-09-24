"""Tests for autonomous research execution-layer policy."""

from research_lab.autonomous_research_orchestrator_execution_layer_policy import (
    evaluate_execution_step,
    validate_execution_layer_policy,
)


def run_tests():
    assert validate_execution_layer_policy() is True

    allowed = evaluate_execution_step("prepare_small_change", cycles_completed=9)
    assert allowed["allowed"] is True
    assert allowed["reason"] == "autonomous_step_allowed"

    exhausted = evaluate_execution_step("prepare_small_change", cycles_completed=10)
    assert exhausted["allowed"] is False
    assert exhausted["stop_required"] is True

    repair_exceeded = evaluate_execution_step("inspect_ci", repair_attempts=2)
    assert repair_exceeded["allowed"] is False

    for step in (
        "change_secrets_or_credentials",
        "execute_supabase_ddl",
        "execute_payment",
        "send_external_notification",
    ):
        result = evaluate_execution_step(step)
        assert result["allowed"] is False
        assert result["human_gate_required"] is True
        assert result["external_action_authorized"] is False

    assert evaluate_execution_step(None)["allowed"] is False
    assert evaluate_execution_step("inspect_state", cycles_completed=True)["allowed"] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer policy tests passed")
