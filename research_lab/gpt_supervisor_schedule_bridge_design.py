"""Bridge GPT supervisor scheduling into Gemini operational assignments.

GPT owns schedule/milestone supervision. Gemini receives a bounded operational
assignment and may prepare implementation work for Codex. This module performs
no scheduling service calls, Gemini API calls, Codex calls, commits, or commerce.
"""

GPT_SUPERVISOR_SCHEDULE_BRIDGE_VERSION = "0.1"

SUPERVISOR_ACTIONS = (
    "assign_operational_goal",
    "hold_for_ci",
    "request_human_gate",
    "close_milestone",
    "advance_milestone",
)

REQUIRED_SUPERVISOR_INPUT = (
    "schedule_tick_id",
    "milestone_id",
    "current_stage",
    "next_theme",
    "latest_ci_green",
    "human_gate_pending",
)

REQUIRED_GEMINI_ASSIGNMENT_FIELDS = (
    "assignment_id",
    "milestone_id",
    "goal",
    "constraints",
    "expected_output",
    "escalation_conditions",
)


def decide_supervisor_action(state):
    if not isinstance(state, dict):
        return {
            "valid": False,
            "action": "hold_for_ci",
            "reason": "state_not_mapping",
        }

    missing = tuple(
        field for field in REQUIRED_SUPERVISOR_INPUT
        if field not in state
    )
    if missing:
        return {
            "valid": False,
            "action": "hold_for_ci",
            "reason": "missing_required_supervisor_input",
            "missing": missing,
        }

    if state.get("human_gate_pending") is True:
        return {
            "valid": True,
            "action": "request_human_gate",
            "reason": "human_gate_pending",
        }

    if state.get("latest_ci_green") is not True:
        return {
            "valid": True,
            "action": "hold_for_ci",
            "reason": "latest_ci_not_green",
        }

    if state.get("milestone_complete") is True:
        return {
            "valid": True,
            "action": "close_milestone",
            "reason": "milestone_complete",
        }

    return {
        "valid": True,
        "action": "assign_operational_goal",
        "reason": "ready_for_next_operational_assignment",
    }


def build_gemini_assignment(state):
    decision = decide_supervisor_action(state)

    if decision.get("action") != "assign_operational_goal":
        return {
            "created": False,
            "decision": decision,
            "assignment": None,
        }

    next_theme = state.get("next_theme")
    assignment_id = (
        f"{state.get('milestone_id')}::{state.get('schedule_tick_id')}::{next_theme}"
    )

    assignment = {
        "assignment_id": assignment_id,
        "milestone_id": state.get("milestone_id"),
        "goal": f"Analyze and prepare the next operational theme: {next_theme}",
        "constraints": (
            "follow_orchestrator_security_policy",
            "do_not_self_authorize_sensitive_actions",
            "do_not_bypass_gpt_supervisor",
            "prepare_codex_task_only_when_code_change_is_needed",
            "escalate_on_policy_ambiguity_or_human_gate",
        ),
        "expected_output": (
            "structured_operational_decision",
            "evidence_summary",
            "recommended_next_action",
            "optional_codex_task_draft",
        ),
        "escalation_conditions": (
            "human_gate_required",
            "policy_ambiguity",
            "repeated_failure",
            "milestone_boundary",
        ),
        "gemini_execution_authorized": False,
        "codex_execution_authorized": False,
        "external_action_authorized": False,
    }

    return {
        "created": True,
        "decision": decision,
        "assignment": assignment,
    }


def validate_gemini_assignment(assignment):
    if not isinstance(assignment, dict):
        return {
            "valid": False,
            "errors": ("assignment_not_mapping",),
        }

    errors = []
    for field in REQUIRED_GEMINI_ASSIGNMENT_FIELDS:
        if field not in assignment:
            errors.append(f"missing_{field}")

    goal = assignment.get("goal")
    if not isinstance(goal, str) or not goal.strip():
        errors.append("invalid_goal")

    constraints = assignment.get("constraints")
    if not isinstance(constraints, (list, tuple)) or not constraints:
        errors.append("invalid_constraints")

    expected_output = assignment.get("expected_output")
    if not isinstance(expected_output, (list, tuple)) or not expected_output:
        errors.append("invalid_expected_output")

    escalation = assignment.get("escalation_conditions")
    if not isinstance(escalation, (list, tuple)) or not escalation:
        errors.append("invalid_escalation_conditions")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "external_action_authorized": False,
    }


def build_gpt_supervisor_schedule_bridge_design():
    return {
        "version": GPT_SUPERVISOR_SCHEDULE_BRIDGE_VERSION,
        "mode": "design_only",
        "supervisor": "gpt",
        "operations_orchestrator": "gemini",
        "implementation_worker": "codex",
        "supervisor_actions": SUPERVISOR_ACTIONS,
        "schedule_tick_required": True,
        "ci_green_required_before_assignment": True,
        "human_gate_preempts_assignment": True,
        "milestone_completion_preempts_assignment": True,
        "gemini_may_bypass_supervisor": False,
        "codex_may_bypass_gemini": False,
        "schedule_service_action_authorized": False,
        "gemini_api_call_authorized": False,
        "codex_invocation_authorized": False,
        "commit_authorized": False,
        "external_action_authorized": False,
    }


def validate_gpt_supervisor_schedule_bridge_design():
    design = build_gpt_supervisor_schedule_bridge_design()
    assert design["mode"] == "design_only"
    assert design["supervisor"] == "gpt"
    assert design["operations_orchestrator"] == "gemini"
    assert design["implementation_worker"] == "codex"
    assert design["ci_green_required_before_assignment"] is True
    assert design["human_gate_preempts_assignment"] is True
    assert design["gemini_may_bypass_supervisor"] is False
    assert design["codex_may_bypass_gemini"] is False
    assert design["schedule_service_action_authorized"] is False
    assert design["gemini_api_call_authorized"] is False
    assert design["codex_invocation_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
