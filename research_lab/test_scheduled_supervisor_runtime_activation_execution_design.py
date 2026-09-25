"""Tests for scheduled supervisor runtime activation execution design."""

from research_lab.scheduled_supervisor_runtime_activation_execution_design import (
    build_activation_execution_design,
    build_activation_execution_plan,
    evaluate_activation_step,
    validate_scheduled_supervisor_runtime_activation_execution_design,
)


def run_tests():
    assert (
        validate_scheduled_supervisor_runtime_activation_execution_design()
        is True
    )

    gate = {
        "approved": True,
        "activation_authorized": True,
    }
    review = {
        "ready_for_activation_gate": True,
    }

    plan = build_activation_execution_plan(gate, review)
    assert plan["valid"] is True
    assert plan["execution_authorized"] is False
    assert plan["runtime_active"] is False
    assert plan["steps"][0] == "activate_scheduler_connector"
    assert plan["steps"][-1] == "enter_runtime_idle"

    first = evaluate_activation_step(plan)
    assert first["action"] == "await_execution"
    assert first["next_step"] == "activate_scheduler_connector"

    partially_completed = (
        "activate_scheduler_connector",
        "verify_scheduler_health",
        "activate_gemini_connector",
    )
    next_step = evaluate_activation_step(
        plan,
        completed_steps=partially_completed,
    )
    assert next_step["next_step"] == "verify_gemini_health"

    failed = evaluate_activation_step(
        plan,
        completed_steps=partially_completed,
        failed_step="verify_gemini_health",
    )
    assert failed["action"] == "rollback"
    assert failed["rollback_required"] is True
    assert failed["rollback_steps"] == (
        "deactivate_gemini_connector",
        "deactivate_scheduler_connector",
    )

    complete = evaluate_activation_step(
        plan,
        completed_steps=plan["steps"],
    )
    assert complete["action"] == "activation_sequence_complete"
    assert complete["runtime_activation_candidate"] is True
    assert complete["execution_authorized"] is False

    blocked = build_activation_execution_plan(
        {"approved": False},
        review,
    )
    assert blocked["valid"] is False
    assert "activation_gate_not_approved" in blocked["errors"]

    design = build_activation_execution_design()
    assert design["fail_closed"] is True
    assert design["partial_activation_enables_runtime"] is False
    assert design["runtime_active"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation execution design tests passed")
