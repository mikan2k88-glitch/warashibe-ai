"""Tests for GPT/Gemini/Codex closed-loop design."""

from research_lab.gpt_gemini_codex_closed_loop_design import (
    build_closed_loop_snapshot,
    evaluate_closed_loop,
    validate_gpt_gemini_codex_closed_loop_design,
)
from research_lab.codex_mcp_result_envelope_design import (
    build_codex_result_envelope,
)


def _state():
    return {
        "schedule_tick_id": "tick-001",
        "milestone_id": "sandbox_external_integration",
        "current_stage": "gemini_operations_assignment_bridge_design",
        "next_theme": "gpt_gemini_codex_closed_loop_design",
        "latest_ci_green": True,
        "human_gate_pending": False,
        "milestone_complete": False,
    }


def _gemini_decision():
    return {
        "assignment_id": "sandbox_external_integration::tick-001::gpt_gemini_codex_closed_loop_design",
        "action": "prepare_codex_task",
        "summary": "Implement the closed-loop integration theme.",
        "confidence": 0.91,
        "evidence_refs": ("schedule:tick-001", "ci:green"),
        "risk_flags": (),
        "requires_human_gate": False,
    }


def _codex_result(branch="research-lab"):
    return build_codex_result_envelope(
        milestone_id="sandbox_external_integration",
        cycle_id="cycle-001",
        task_id="task-001",
        status="completed",
        branch=branch,
        changed_files=("research_lab/example.py",),
        test_command="python -m research_lab.runner",
        test_passed=True,
        diff_summary="Implemented closed-loop integration.",
        acceptance_checks={"offline_tests_green": "passed"},
    )


def run_tests():
    assert validate_gpt_gemini_codex_closed_loop_design() is True

    awaiting_gemini = evaluate_closed_loop(_state())
    assert awaiting_gemini["status"] == "awaiting_gemini_decision"
    assert awaiting_gemini["next_action"] == "await_gemini"

    awaiting_codex = evaluate_closed_loop(
        _state(),
        gemini_decision=_gemini_decision(),
        branch="research-lab",
        requested_capabilities=(
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    assert awaiting_codex["status"] == "awaiting_codex_result"
    assert awaiting_codex["next_action"] == "await_codex"

    reviewed = evaluate_closed_loop(
        _state(),
        gemini_decision=_gemini_decision(),
        codex_result=_codex_result(),
        branch="research-lab",
        requested_capabilities=(
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    assert reviewed["status"] == "closed_loop_reviewed"
    assert reviewed["next_action"] == "commit_review"

    main_reviewed = evaluate_closed_loop(
        _state(),
        gemini_decision=_gemini_decision(),
        codex_result=_codex_result("main"),
        branch="main",
        requested_capabilities=(
            "modify_main_branch_code",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    assert main_reviewed["next_action"] == "request_main_write_gate"

    held_state = _state()
    held_state["latest_ci_green"] = False
    held = evaluate_closed_loop(held_state)
    assert held["status"] == "supervisor_terminal"
    assert held["next_action"] == "hold_for_ci"

    snapshot = build_closed_loop_snapshot()
    assert snapshot["supervisor"] == "gpt"
    assert snapshot["operations_orchestrator"] == "gemini"
    assert snapshot["implementation_worker"] == "codex"
    assert snapshot["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("GPT Gemini Codex closed loop design tests passed")
