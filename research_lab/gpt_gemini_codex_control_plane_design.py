"""Organizational control-plane design for Warashibe AI.

Role model:
- HUMAN: owner / final authority.
- GPT Supervisor: schedule, milestones, supervision, escalation.
- Gemini Orchestrator: day-to-day operational reasoning and task preparation.
- Codex: implementation worker for code changes.
- Safety Kernel / CI: policy enforcement and verification.

This module defines authority boundaries only. It performs no external action.
"""

CONTROL_PLANE_VERSION = "0.1"

ROLES = {
    "human_owner": {
        "role": "owner",
        "may_approve_human_gates": True,
        "may_override_schedule": True,
        "may_authorize_main_write": True,
    },
    "gpt_supervisor": {
        "role": "supervisor_scheduler",
        "may_set_milestones": True,
        "may_select_next_theme": True,
        "may_assign_gemini_work": True,
        "may_review_ci": True,
        "may_escalate_to_human": True,
        "may_directly_execute_commerce": False,
    },
    "gemini_orchestrator": {
        "role": "operations_orchestrator",
        "may_analyze_market_state": True,
        "may_rank_candidates": True,
        "may_prepare_codex_tasks": True,
        "may_prepare_executor_requests": True,
        "may_escalate_to_supervisor": True,
        "may_self_authorize_sensitive_actions": False,
    },
    "codex_worker": {
        "role": "implementation_worker",
        "may_edit_repository_code": True,
        "may_run_tests": True,
        "may_report_results": True,
        "may_self_authorize_policy_override": False,
    },
    "safety_kernel_ci": {
        "role": "independent_control",
        "may_validate_policy": True,
        "may_block_progress": True,
        "may_validate_tests": True,
        "may_grant_human_authority": False,
    },
}

AUTHORITY_CHAIN = (
    "human_owner",
    "gpt_supervisor",
    "gemini_orchestrator",
    "codex_worker",
)

CONTROL_FLOW = (
    "gpt_supervisor_checks_schedule_ci_and_milestone",
    "gpt_supervisor_assigns_operational_goal",
    "gemini_orchestrator_analyzes_and_prepares_task",
    "safety_kernel_validates_task",
    "codex_worker_implements_code_change",
    "safety_kernel_ci_validates_result",
    "gemini_orchestrator_summarizes_operational_result",
    "gpt_supervisor_decides_next_theme_or_escalation",
    "human_owner_handles_human_gate_when_required",
)

ESCALATION_RULES = {
    "gemini_to_gpt": (
        "uncertain_strategy",
        "milestone_boundary",
        "repeated_failure",
        "policy_ambiguity",
    ),
    "gpt_to_human": (
        "main_branch_write",
        "secrets_or_credentials",
        "production_change",
        "commerce_or_payment",
        "live_external_api_activation",
        "privilege_expansion",
    ),
}


def build_control_plane_design():
    return {
        "version": CONTROL_PLANE_VERSION,
        "mode": "design_only",
        "roles": ROLES,
        "authority_chain": AUTHORITY_CHAIN,
        "control_flow": CONTROL_FLOW,
        "escalation_rules": ESCALATION_RULES,
        "gpt_is_supervisor": True,
        "gemini_is_operations_layer": True,
        "codex_is_implementation_layer": True,
        "safety_kernel_is_independent_control": True,
        "human_is_final_authority": True,
        "gemini_may_bypass_gpt": False,
        "codex_may_bypass_gemini": False,
        "codex_may_bypass_safety_kernel": False,
        "external_action_authorized": False,
    }


def validate_control_plane_design():
    design = build_control_plane_design()
    assert design["gpt_is_supervisor"] is True
    assert design["gemini_is_operations_layer"] is True
    assert design["codex_is_implementation_layer"] is True
    assert design["safety_kernel_is_independent_control"] is True
    assert design["human_is_final_authority"] is True
    assert design["gemini_may_bypass_gpt"] is False
    assert design["codex_may_bypass_gemini"] is False
    assert design["codex_may_bypass_safety_kernel"] is False
    assert design["authority_chain"] == (
        "human_owner",
        "gpt_supervisor",
        "gemini_orchestrator",
        "codex_worker",
    )
    assert design["external_action_authorized"] is False
    return True
