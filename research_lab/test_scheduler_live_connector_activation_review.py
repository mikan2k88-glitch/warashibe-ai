"""Checks for the scheduler connector activation review."""

from research_lab.scheduler_live_connector_activation_review import review_scheduler_activation
from research_lab.scheduler_live_connector_implementation_design import build_scheduler_trigger


def run_tests():
    trigger = build_scheduler_trigger(
        "tick-001", "recurring_schedule", "2026-09-25T21:00:00+09:00",
        "supervisory_closed_loop", ("inspect_state", "inspect_ci"),
    )
    ready = review_scheduler_activation(trigger, ci_green=True, connector_verified=True,
                                        healthcheck_passed=True, human_gate=False)
    assert ready["ready_for_activation_gate"] is True
    assert ready["activation_authorized"] is False
    assert ready["external_action_authorized"] is False

    for override, blocker in (
        ({"ci_green": False}, "latest_ci_not_green"),
        ({"connector_verified": False}, "connector_not_verified"),
        ({"healthcheck_passed": False}, "healthcheck_not_passed"),
        ({"human_gate": True}, "human_gate_active"),
    ):
        inputs = dict(ci_green=True, connector_verified=True,
                      healthcheck_passed=True, human_gate=False)
        inputs.update(override)
        report = review_scheduler_activation(trigger, **inputs)
        assert report["ready_for_activation_gate"] is False
        assert blocker in report["blockers"]
        assert report["activation_authorized"] is False

    malformed = dict(trigger, requested_scope=("purchase_item",))
    assert "invalid_trigger" in review_scheduler_activation(
        malformed, True, True, True, False)["blockers"]
    assert review_scheduler_activation(trigger, 1, True, True, False)[
        "ready_for_activation_gate"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduler activation review tests passed")
