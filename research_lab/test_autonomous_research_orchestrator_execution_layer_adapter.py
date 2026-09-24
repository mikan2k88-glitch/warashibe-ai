"""Tests for the autonomous research execution-layer adapter."""

from research_lab.autonomous_research_orchestrator_execution_layer_adapter import (
    build_execution_adapter,
    validate_execution_layer_adapter,
)


def run_tests():
    assert validate_execution_layer_adapter() is True

    adapter = build_execution_adapter(cycles_completed=2)
    assert adapter["ready"] is True
    assert adapter["research_branch_only"] is True
    assert adapter["request_count"] == len(adapter["requests"])
    assert adapter["requests"][0]["step"] == "inspect_state"
    assert adapter["requests"][-1]["step"] == "record_progress"

    exhausted = build_execution_adapter(cycles_completed=10)
    assert exhausted["ready"] is False
    assert exhausted["request_count"] == 0

    repair_exceeded = build_execution_adapter(repair_attempts=2)
    assert repair_exceeded["ready"] is False

    for key in (
        "external_action_authorized",
        "external_action_performed",
        "credentials_included",
        "production_changed",
        "commerce_executed",
    ):
        assert adapter[key] is False


if __name__ == "__main__":
    run_tests()
    print("autonomous research orchestrator execution layer adapter tests passed")
