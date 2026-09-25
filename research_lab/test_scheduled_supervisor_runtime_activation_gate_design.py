"""Tests for scheduled GPT Supervisor runtime activation gate design."""

from research_lab.scheduled_supervisor_runtime_activation_gate_design import (
    build_activation_gate_design,
    build_activation_gate_snapshot,
    evaluate_activation_gate,
    validate_scheduled_supervisor_runtime_activation_gate_design,
)


def run_tests():
    assert validate_scheduled_supervisor_runtime_activation_gate_design() is True

    closed = build_activation_gate_snapshot()
    closed_result = evaluate_activation_gate(closed)
    assert closed["all_design_gates_green"] is True
    assert closed["all_safety_gates_green"] is True
    assert closed["all_live_gates_green"] is False
    assert closed_result["approved"] is False
    assert "live_connectors_not_ready" in closed_result["blockers"]
    assert "explicit_human_approval_required" in closed_result["blockers"]

    live_without_human = build_activation_gate_snapshot(
        live_scheduler_connected=True,
        live_gemini_connected=True,
        live_codex_connected=True,
    )
    live_without_human_result = evaluate_activation_gate(live_without_human)
    assert live_without_human_result["approved"] is False
    assert live_without_human_result["blockers"] == (
        "explicit_human_approval_required",
    )

    fully_approved = build_activation_gate_snapshot(
        live_scheduler_connected=True,
        live_gemini_connected=True,
        live_codex_connected=True,
        explicit_human_approval=True,
    )
    approved_result = evaluate_activation_gate(fully_approved)
    assert approved_result["approved"] is True
    assert approved_result["approval_scope"] == (
        "scheduled_supervisor_runtime_activation"
    )
    assert approved_result["approval_reusable"] is False
    assert approved_result["activation_authorized"] is False
    assert approved_result["evidence_verified"] is False
    assert approved_result["scheduled_runtime_active"] is False
    assert approved_result["external_action_authorized"] is False

    forged = {
        "all_design_gates_green": True,
        "all_safety_gates_green": True,
        "all_live_gates_green": True,
        "explicit_human_approval": True,
    }
    forged_result = evaluate_activation_gate(forged)
    assert forged_result["approved"] is False
    assert forged_result["activation_authorized"] is False

    design = build_activation_gate_design()
    assert design["explicit_human_approval_required"] is True
    assert design["activation_is_separate_from_gate_evaluation"] is True
    assert design["scheduled_runtime_active"] is False


if __name__ == "__main__":
    run_tests()
    print("Scheduled supervisor runtime activation gate design tests passed")
