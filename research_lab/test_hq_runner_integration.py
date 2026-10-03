"""P1 HQ-to-runner integration contract tests."""

from research_lab.runner import build_hq_runner_handoff


def main():
    scheduled = build_hq_runner_handoff(
        event="schedule",
        passed=True,
        profile="build",
        operational_evidence={
            "hq_runner_integrated": True,
            "real_pilot_decision_packet_ready": False,
            "ceo_approval_gate_ready": False,
            "live_pilot_verified": False,
            "learning_feedback_ingested": False,
            "capital_velocity_optimized": False,
            "controlled_automation_scope_ready": False,
        },
    )
    assert scheduled["stage"] == "hq_priority_selected"
    assert scheduled["selected_priority"] == "P2"
    assert scheduled["next_action"] == "execute_real_pilot_readiness"
    assert scheduled["human_gate_preserved"] is True
    assert scheduled["external_execution_authorized"] is False

    failed = build_hq_runner_handoff(
        event="schedule",
        passed=False,
        profile="build",
        operational_evidence={"hq_runner_integrated": True},
    )
    assert failed["stage"] == "targeted_checks_failed"
    assert failed["next_action"] == "repair_current_problem"

    print("P1 HQ-to-runner integration tests passed")


if __name__ == "__main__":
    main()
