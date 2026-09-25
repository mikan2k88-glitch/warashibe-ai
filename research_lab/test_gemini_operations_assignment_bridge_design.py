"""Tests for Gemini operations assignment bridge design."""

from research_lab.gemini_operations_assignment_bridge_design import (
    build_gemini_operations_assignment_bridge_design,
    process_gemini_assignment,
    validate_gemini_operational_decision,
    validate_gemini_operations_assignment_bridge_design,
)
from research_lab.gpt_supervisor_schedule_bridge_design import build_gemini_assignment


def _assignment():
    state = {
        "schedule_tick_id": "tick-001",
        "milestone_id": "sandbox_external_integration",
        "current_stage": "gpt_supervisor_schedule_bridge_design",
        "next_theme": "gemini_operations_assignment_bridge_design",
        "latest_ci_green": True,
        "human_gate_pending": False,
        "milestone_complete": False,
    }
    return build_gemini_assignment(state)["assignment"]


def _decision(action="prepare_codex_task", requires_human_gate=False):
    return {
        "assignment_id": "sandbox_external_integration::tick-001::gemini_operations_assignment_bridge_design",
        "action": action,
        "summary": "Implement the next bounded integration theme.",
        "confidence": 0.9,
        "evidence_refs": ("schedule:tick-001", "ci:green"),
        "risk_flags": (),
        "requires_human_gate": requires_human_gate,
    }


def run_tests():
    assert validate_gemini_operations_assignment_bridge_design() is True

    decision_validation = validate_gemini_operational_decision(_decision())
    assert decision_validation["valid"] is True

    ready = process_gemini_assignment(
        _assignment(),
        _decision(),
        cycle_id="cycle-001",
        task_id="task-001",
        branch="research-lab",
        requested_capabilities=(
            "inspect_repository",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    assert ready["status"] == "codex_task_ready"
    assert ready["codex_task_validation"]["valid"] is True
    assert ready["codex_task"]["branch"] == "research-lab"
    assert ready["gemini_execution_authorized"] is False
    assert ready["codex_execution_authorized"] is False

    main_ready = process_gemini_assignment(
        _assignment(),
        _decision(),
        cycle_id="cycle-002",
        task_id="task-main-001",
        branch="main",
        requested_capabilities=(
            "modify_main_branch_code",
            "edit_code_files",
            "run_offline_tests",
        ),
        acceptance_checks=("offline_tests_green",),
    )
    assert main_ready["status"] == "codex_task_ready"
    assert main_ready["codex_task"]["branch"] == "main"

    escalated = process_gemini_assignment(
        _assignment(),
        _decision(action="escalate_to_gpt"),
        cycle_id="cycle-003",
        task_id="task-escalate",
    )
    assert escalated["status"] == "escalate_to_gpt"
    assert escalated["codex_task"] is None

    human_gate = process_gemini_assignment(
        _assignment(),
        _decision(action="request_human_gate", requires_human_gate=True),
        cycle_id="cycle-004",
        task_id="task-gate",
    )
    assert human_gate["status"] == "human_gate_required"
    assert human_gate["codex_task"] is None

    design = build_gemini_operations_assignment_bridge_design()
    assert design["supervisor"] == "gpt"
    assert design["operations_owner"] == "gemini"
    assert design["implementation_worker"] == "codex"
    assert design["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("Gemini operations assignment bridge design tests passed")
