"""Milestone validation for the Warashibe AI supervisory closed loop.

Validates the designed path:
User/Chat -> GPT Supervisor -> Gemini Operations -> Codex -> Review -> GPT,
with Safety/CI controls and HUMAN GATE boundaries preserved.

No external APIs, scheduler services, Codex process, commits, or commerce are
executed by this module.
"""

from research_lab.chat_supervisor_command_bridge_design import (
    build_supervisor_command,
    route_supervisor_command,
    validate_chat_supervisor_command_bridge_design,
)
from research_lab.gpt_gemini_codex_control_plane_design import (
    validate_control_plane_design,
)
from research_lab.gpt_supervisor_schedule_bridge_design import (
    build_gemini_assignment,
    validate_gpt_supervisor_schedule_bridge_design,
)
from research_lab.gemini_operations_assignment_bridge_design import (
    process_gemini_assignment,
    validate_gemini_operations_assignment_bridge_design,
)
from research_lab.gpt_gemini_codex_closed_loop_design import (
    evaluate_closed_loop,
    validate_gpt_gemini_codex_closed_loop_design,
)
from research_lab.codex_mcp_result_envelope_design import (
    build_codex_result_envelope,
)
from research_lab.codex_mcp_commit_controller_design import (
    decide_commit_action,
    validate_codex_mcp_commit_controller_design,
)

CLOSED_LOOP_MILESTONE_VALIDATION_VERSION = "0.1"

MILESTONE_COMPONENTS = (
    "chat_supervisor_command_bridge",
    "gpt_gemini_codex_control_plane",
    "gpt_supervisor_schedule_bridge",
    "gemini_operations_assignment_bridge",
    "gpt_gemini_codex_closed_loop",
    "codex_mcp_commit_controller",
)


def _supervisor_state():
    return {
        "schedule_tick_id": "milestone-tick-001",
        "milestone_id": "supervisory_closed_loop",
        "current_stage": "closed_loop_milestone_validation",
        "next_theme": "scheduled_supervisor_runtime_activation_review",
        "latest_ci_green": True,
        "human_gate_pending": False,
        "milestone_complete": False,
    }


def _gemini_decision():
    return {
        "assignment_id": (
            "supervisory_closed_loop::milestone-tick-001::"
            "scheduled_supervisor_runtime_activation_review"
        ),
        "action": "prepare_codex_task",
        "summary": "Prepare the next bounded supervisory runtime theme.",
        "confidence": 0.95,
        "evidence_refs": ("ci:green", "milestone:supervisory_closed_loop"),
        "risk_flags": (),
        "requires_human_gate": False,
    }


def _codex_result(branch="research-lab"):
    return build_codex_result_envelope(
        milestone_id="supervisory_closed_loop",
        cycle_id="cycle-001",
        task_id="task-001",
        status="completed",
        branch=branch,
        changed_files=("research_lab/example.py",),
        test_command="python -m research_lab.runner",
        test_passed=True,
        diff_summary="Completed bounded milestone validation fixture.",
        acceptance_checks={"offline_tests_green": "passed"},
    )


def validate_closed_loop_milestone():
    component_checks = {
        "chat_supervisor_command_bridge":
            validate_chat_supervisor_command_bridge_design(),
        "gpt_gemini_codex_control_plane":
            validate_control_plane_design(),
        "gpt_supervisor_schedule_bridge":
            validate_gpt_supervisor_schedule_bridge_design(),
        "gemini_operations_assignment_bridge":
            validate_gemini_operations_assignment_bridge_design(),
        "gpt_gemini_codex_closed_loop":
            validate_gpt_gemini_codex_closed_loop_design(),
        "codex_mcp_commit_controller":
            validate_codex_mcp_commit_controller_design(),
    }

    command = build_supervisor_command(
        command_id="chat-milestone-001",
        intent="Continue bounded autonomous development.",
        target_milestone="supervisory_closed_loop",
        requested_scope=("research_lab",),
        delivery_mode="next_schedule_tick",
    )
    command_route = route_supervisor_command(command)

    state = _supervisor_state()
    assignment = build_gemini_assignment(state)["assignment"]

    gemini = process_gemini_assignment(
        assignment,
        _gemini_decision(),
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

    loop = evaluate_closed_loop(
        state,
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

    commit = decide_commit_action(
        loop["codex_review"],
        orchestrator_approved=True,
    )

    main_loop = evaluate_closed_loop(
        state,
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

    checks = {
        "all_component_designs_valid": all(component_checks.values()),
        "chat_command_can_wait_for_schedule":
            command_route["status"] == "queued_for_supervisor_tick",
        "gpt_can_create_gemini_assignment": assignment is not None,
        "gemini_can_prepare_codex_task":
            gemini["status"] == "codex_task_ready",
        "research_loop_reaches_commit_review":
            loop["next_action"] == "commit_review",
        "research_commit_requires_orchestrator":
            commit["action"] == "prepare_research_lab_commit"
            and commit["commit_authorized"] is False,
        "main_loop_stops_at_human_gate":
            main_loop["next_action"] == "request_main_write_gate",
    }

    passed = all(checks.values())

    return {
        "version": CLOSED_LOOP_MILESTONE_VALIDATION_VERSION,
        "milestone": "supervisory_closed_loop",
        "passed": passed,
        "component_checks": component_checks,
        "checks": checks,
        "validated_path": (
            "user_chat",
            "gpt_supervisor",
            "gemini_orchestrator",
            "codex_worker",
            "safety_ci_review",
            "gpt_supervisor_followup",
        ),
        "human_final_authority": True,
        "live_scheduler_connected": False,
        "live_gemini_connected": False,
        "live_codex_connected": False,
        "external_action_authorized": False,
    }


def validate_closed_loop_milestone_validation():
    report = validate_closed_loop_milestone()
    assert report["passed"] is True
    assert report["human_final_authority"] is True
    assert report["live_scheduler_connected"] is False
    assert report["live_gemini_connected"] is False
    assert report["live_codex_connected"] is False
    assert report["external_action_authorized"] is False
    return True
