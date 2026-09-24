"""Offline tests for the autonomous research state machine."""

from research_lab.autonomous_research_state_machine import (
    STATES,
    STATE_MACHINE_VERSION,
    next_state,
    validate_state_machine,
)


def main():
    assert STATE_MACHINE_VERSION == "0.1"
    assert validate_state_machine() is True
    assert set(STATES) == {
        "inspect",
        "work",
        "verify_ci",
        "repair",
        "human_gate",
        "stopped",
    }

    assert next_state("inspect", action="modify_main_branch") == "human_gate"
    assert next_state("inspect", action="execute_payment") == "human_gate"
    assert next_state("invalid_state") == "stopped"
    assert next_state("verify_ci", ci_status="pending") == "verify_ci"

    print("Autonomous research state machine tests passed")


if __name__ == "__main__":
    main()
