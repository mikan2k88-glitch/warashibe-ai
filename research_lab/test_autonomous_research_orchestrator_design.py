"""Offline tests for the autonomous research orchestrator design."""

from research_lab.autonomous_research_orchestrator_design import (
    AUTONOMOUS_ACTIONS,
    HUMAN_GATE_ACTIONS,
    ORCHESTRATOR_DESIGN_VERSION,
    STOP_CONDITIONS,
    classify_action,
    validate_orchestrator_design,
)


def main():
    assert ORCHESTRATOR_DESIGN_VERSION == "0.1"
    assert validate_orchestrator_design() is True
    assert AUTONOMOUS_ACTIONS
    assert HUMAN_GATE_ACTIONS
    assert STOP_CONDITIONS

    for action in AUTONOMOUS_ACTIONS:
        assert classify_action(action) == "autonomous"

    for action in HUMAN_GATE_ACTIONS:
        assert classify_action(action) == "human_gate"

    assert classify_action("deploy_unknown_system") == "stop_unknown"

    print("Autonomous research orchestrator design tests passed")


if __name__ == "__main__":
    main()
