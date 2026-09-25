"""Closed-loop development control design for GPT -> Gemini -> Codex -> GPT.

The loop coordinates supervision, operational reasoning, implementation results,
and escalation. It remains design-only and performs no external execution.
"""

from research_lab.gpt_supervisor_schedule_bridge_design import (
    build_gemini_assignment,
    decide_supervisor_action,
)
from research_lab.gemini_operations_assignment_bridge_design import (
    process_gemini_assignment,
)
from research_lab.codex_mcp_orchestrator_review_bridge_design import (
    review_codex_result,
)

GPT_GEMINI_CODEX_CLOSED_LOOP_VERSION = "0.1"

LOOP_STAGES = (
    "gpt_supervisor_decision",
    "gemini_assignment",
    "gemini_operational_decision",
    "codex_task_preparation",
    "codex_execution_result",
    "orchestrator_result_review",
    "gpt_supervisor_followup",
)

TERMINAL_ACTIONS = (
    "hold_for_ci",
    "request_human_gate",
    "close_milestone",
    "stop",
)


def build_closed_loop_snapshot():
    return {
        "version": GPT_GEMINI_CODEX_CLOSED_LOOP_VERSION,
        "mode": "design_only",
        "loop_stages": LOOP_STAGES,
        "terminal_actions": TERMINAL_ACTIONS,
        "supervisor": "gpt",
        "operations_orchestrator": "gemini",
        "implementation_worker": "codex",
        "independent_control": "safety_kernel_ci",
        "human_final_authority": True,
        "max_repairs_per_cycle": 1,
        "ci_green_required_before_next_cycle": True,
        "gemini_may_bypass_gpt": False,
        "codex_may_bypass_gemini": False,
        "codex_may_self_commit": False,
        "main_write_requires_human_gate": True,
        "external_action_authorized": False,
    }


def evaluate_closed_loop(
    supervisor_state,
    gemini_decision=None,
    codex_result=None,
    cycle_id="cycle-001",
    task_id="task-001",
    branch="research-lab",
    requested_capabilities=(),
    acceptance_checks=(),
    repairs_used=0,
):
    supervisor = decide_supervisor_action(supervisor_state)

    if supervisor.get("action") != "assign_operational_goal":
        return {
            "status": "supervisor_terminal",
            "supervisor": supervisor,
            "assignment": None,
            "gemini": None,
            "codex_review": None,
            "next_action": supervisor.get("action"),
            "external_action_authorized": False,
        }

    assignment_result = build_gemini_assignment(supervisor_state)
    assignment = assignment_result.get("assignment")

    if gemini_decision is None:
        return {
            "status": "awaiting_gemini_decision",
            "supervisor": supervisor,
            "assignment": assignment,
            "gemini": None,
            "codex_review": None,
            "next_action": "await_gemini",
            "external_action_authorized": False,
        }

    gemini = process_gemini_assignment(
        assignment,
        gemini_decision,
        cycle_id=cycle_id,
        task_id=task_id,
        branch=branch,
        requested_capabilities=requested_capabilities,
        acceptance_checks=acceptance_checks,
    )

    if gemini.get("status") != "codex_task_ready":
        return {
            "status": "gemini_terminal",
            "supervisor": supervisor,
            "assignment": assignment,
            "gemini": gemini,
            "codex_review": None,
            "next_action": gemini.get("status"),
            "external_action_authorized": False,
        }

    if codex_result is None:
        return {
            "status": "awaiting_codex_result",
            "supervisor": supervisor,
            "assignment": assignment,
            "gemini": gemini,
            "codex_review": None,
            "next_action": "await_codex",
            "external_action_authorized": False,
        }

    codex_review = review_codex_result(
        codex_result,
        repairs_used=repairs_used,
    )

    return {
        "status": "closed_loop_reviewed",
        "supervisor": supervisor,
        "assignment": assignment,
        "gemini": gemini,
        "codex_review": codex_review,
        "next_action": codex_review.get("action"),
        "external_action_authorized": False,
    }


def validate_gpt_gemini_codex_closed_loop_design():
    snapshot = build_closed_loop_snapshot()
    assert snapshot["mode"] == "design_only"
    assert snapshot["supervisor"] == "gpt"
    assert snapshot["operations_orchestrator"] == "gemini"
    assert snapshot["implementation_worker"] == "codex"
    assert snapshot["independent_control"] == "safety_kernel_ci"
    assert snapshot["human_final_authority"] is True
    assert snapshot["max_repairs_per_cycle"] == 1
    assert snapshot["ci_green_required_before_next_cycle"] is True
    assert snapshot["gemini_may_bypass_gpt"] is False
    assert snapshot["codex_may_bypass_gemini"] is False
    assert snapshot["codex_may_self_commit"] is False
    assert snapshot["main_write_requires_human_gate"] is True
    assert snapshot["external_action_authorized"] is False
    return True
