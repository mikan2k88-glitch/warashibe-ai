"""Tests for bounded executor controller validation."""

from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_controller import (
    control_bounded_executor_cycle,
)
from research_lab.autonomous_research_orchestrator_execution_layer_bounded_executor_controller_validation import (
    validate_bounded_executor_controller_output,
)


def run_tests():
    ready = control_bounded_executor_cycle(cycles_completed=9, repair_attempts=1)
    result = validate_bounded_executor_controller_output(ready)
    assert result["valid"] is True
    assert result["ready_for_next_boundary"] is True
    assert result["external_action_authorized"] is False

    exhausted = control_bounded_executor_cycle(cycles_completed=10)
    result = validate_bounded_executor_controller_output(exhausted)
    assert result["valid"] is True
    assert result["ready_for_next_boundary"] is False

    tampered = dict(ready)
    tampered["branch"] = "main"
    assert validate_bounded_executor_controller_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["executor_invoked"] = True
    assert validate_bounded_executor_controller_output(tampered)["valid"] is False

    tampered = dict(ready)
    tampered["commerce_authorized"] = True
    assert validate_bounded_executor_controller_output(tampered)["valid"] is False

    assert validate_bounded_executor_controller_output(None)["valid"] is False


if __name__ == "__main__":
    run_tests()
    print("bounded executor controller validation tests passed")
