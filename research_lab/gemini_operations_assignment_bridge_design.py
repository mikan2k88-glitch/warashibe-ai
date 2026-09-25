"""Translate GPT supervisor assignments into Gemini operational decisions.

Gemini acts as the operations layer: it analyzes an assignment, produces a
bounded structured decision, and may draft a Codex task envelope when code work
is required. This module performs no Gemini or Codex API calls.
"""

from research_lab.codex_mcp_task_envelope_design import (
    build_codex_task_envelope,
    validate_codex_task_envelope,
)
from research_lab.gpt_supervisor_schedule_bridge_design import (
    validate_gemini_assignment,
)

GEMINI_OPERATIONS_ASSIGNMENT_BRIDGE_VERSION = "0.1"

ALLOWED_OPERATIONAL_ACTIONS = (
    "analyze_only",
    "prepare_codex_task",
    "request_more_evidence",
    "escalate_to_gpt",
    "request_human_gate",
)

REQUIRED_DECISION_FIELDS = (
    "assignment_id",
    "action",
    "summary",
    "confidence",
    "evidence_refs",
    "risk_flags",
    "requires_human_gate",
)


def validate_gemini_operational_decision(decision):
    if not isinstance(decision, dict):
        return {
            "valid": False,
            "errors": ("decision_not_mapping",),
        }

    errors = []

    for field in REQUIRED_DECISION_FIELDS:
        if field not in decision:
            errors.append(f"missing_{field}")

    if decision.get("action") not in ALLOWED_OPERATIONAL_ACTIONS:
        errors.append("unsupported_action")

    summary = decision.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("invalid_summary")

    confidence = decision.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("invalid_confidence")
    elif not 0 <= confidence <= 1:
        errors.append("confidence_out_of_range")

    refs = decision.get("evidence_refs")
    if not isinstance(refs, (list, tuple)):
        errors.append("invalid_evidence_refs")

    risk_flags = decision.get("risk_flags")
    if not isinstance(risk_flags, (list, tuple)):
        errors.append("invalid_risk_flags")

    if not isinstance(decision.get("requires_human_gate"), bool):
        errors.append("invalid_requires_human_gate")

    return {
        "valid": not errors,
        "errors": tuple(dict.fromkeys(errors)),
    }


def process_gemini_assignment(
    assignment,
    decision,
    cycle_id,
    task_id,
    branch="research-lab",
    requested_capabilities=(),
    acceptance_checks=(),
):
    assignment_validation = validate_gemini_assignment(assignment)
    if not assignment_validation.get("valid"):
        return {
            "status": "rejected_assignment",
            "assignment_validation": assignment_validation,
            "decision_validation": None,
            "codex_task": None,
            "external_action_authorized": False,
        }

    decision_validation = validate_gemini_operational_decision(decision)
    if not decision_validation.get("valid"):
        return {
            "status": "rejected_decision",
            "assignment_validation": assignment_validation,
            "decision_validation": decision_validation,
            "codex_task": None,
            "external_action_authorized": False,
        }

    action = decision.get("action")

    if action == "request_human_gate" or decision.get("requires_human_gate") is True:
        return {
            "status": "human_gate_required",
            "assignment_validation": assignment_validation,
            "decision_validation": decision_validation,
            "codex_task": None,
            "external_action_authorized": False,
        }

    if action in ("escalate_to_gpt", "request_more_evidence", "analyze_only"):
        return {
            "status": action,
            "assignment_validation": assignment_validation,
            "decision_validation": decision_validation,
            "codex_task": None,
            "external_action_authorized": False,
        }

    if action != "prepare_codex_task":
        return {
            "status": "unsupported_operational_path",
            "assignment_validation": assignment_validation,
            "decision_validation": decision_validation,
            "codex_task": None,
            "external_action_authorized": False,
        }

    task = build_codex_task_envelope(
        milestone_id=assignment["milestone_id"],
        cycle_id=cycle_id,
        task_id=task_id,
        goal=decision["summary"],
        branch=branch,
        requested_capabilities=requested_capabilities,
        acceptance_checks=acceptance_checks,
        human_gate_approved=False,
    )
    task_validation = validate_codex_task_envelope(task)

    return {
        "status": (
            "codex_task_ready"
            if task_validation.get("valid")
            else "codex_task_rejected"
        ),
        "assignment_validation": assignment_validation,
        "decision_validation": decision_validation,
        "codex_task": task,
        "codex_task_validation": task_validation,
        "gemini_execution_authorized": False,
        "codex_execution_authorized": False,
        "external_action_authorized": False,
    }


def build_gemini_operations_assignment_bridge_design():
    return {
        "version": GEMINI_OPERATIONS_ASSIGNMENT_BRIDGE_VERSION,
        "mode": "design_only",
        "operations_owner": "gemini",
        "supervisor": "gpt",
        "implementation_worker": "codex",
        "allowed_operational_actions": ALLOWED_OPERATIONAL_ACTIONS,
        "structured_decision_required": True,
        "codex_task_must_use_canonical_envelope": True,
        "human_gate_preempts_codex_task": True,
        "gemini_may_self_execute_code": False,
        "gemini_may_self_authorize_sensitive_actions": False,
        "gemini_api_call_authorized": False,
        "codex_invocation_authorized": False,
        "external_action_authorized": False,
    }


def validate_gemini_operations_assignment_bridge_design():
    design = build_gemini_operations_assignment_bridge_design()
    assert design["mode"] == "design_only"
    assert design["operations_owner"] == "gemini"
    assert design["supervisor"] == "gpt"
    assert design["implementation_worker"] == "codex"
    assert design["structured_decision_required"] is True
    assert design["codex_task_must_use_canonical_envelope"] is True
    assert design["human_gate_preempts_codex_task"] is True
    assert design["gemini_may_self_execute_code"] is False
    assert design["gemini_may_self_authorize_sensitive_actions"] is False
    assert design["gemini_api_call_authorized"] is False
    assert design["codex_invocation_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
