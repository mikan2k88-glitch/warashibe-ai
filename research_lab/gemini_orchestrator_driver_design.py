"""Design Gemini as a pluggable reasoning driver for the Warashibe Orchestrator.

This module is design-only. It performs no network calls and grants no
execution authority. Gemini may propose decisions, but policy and execution
remain outside the model boundary.
"""

GEMINI_ORCHESTRATOR_DRIVER_VERSION = "0.1"

ALLOWED_DECISION_TYPES = (
    "select_next_theme",
    "rank_candidates",
    "summarize_market_evidence",
    "propose_risk_action",
    "propose_kaizen_experiment",
    "prepare_executor_request",
    "analyze_ci_failure",
)

FORBIDDEN_DIRECT_ACTIONS = (
    "purchase_item",
    "list_item",
    "send_payment",
    "issue_refund",
    "modify_secret",
    "modify_production",
    "modify_main_branch",
    "invoke_unbounded_executor",
)

REQUIRED_DECISION_FIELDS = (
    "decision_type",
    "summary",
    "recommended_action",
    "confidence",
    "evidence_refs",
    "requires_human_gate",
)


def validate_driver_decision(payload):
    errors = []

    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ("decision_not_mapping",),
            "execution_authorized": False,
        }

    for field in REQUIRED_DECISION_FIELDS:
        if field not in payload:
            errors.append(f"missing_{field}")

    decision_type = payload.get("decision_type")
    if decision_type not in ALLOWED_DECISION_TYPES:
        errors.append("unsupported_decision_type")

    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("invalid_confidence")
    elif not 0 <= confidence <= 1:
        errors.append("confidence_out_of_range")

    evidence_refs = payload.get("evidence_refs")
    if not isinstance(evidence_refs, (list, tuple)):
        errors.append("invalid_evidence_refs")

    if payload.get("recommended_action") in FORBIDDEN_DIRECT_ACTIONS:
        errors.append("forbidden_direct_action")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "execution_authorized": False,
        "requires_policy_validation": True,
    }


def build_gemini_orchestrator_driver_design():
    return {
        "version": GEMINI_ORCHESTRATOR_DRIVER_VERSION,
        "mode": "design_only",
        "role": "reasoning_driver",
        "allowed_decision_types": ALLOWED_DECISION_TYPES,
        "forbidden_direct_actions": FORBIDDEN_DIRECT_ACTIONS,
        "required_decision_fields": REQUIRED_DECISION_FIELDS,
        "model_primary": "gemini-3.8-flash",
        "model_fallbacks": ("gemini-3.7-flash", "gemini-3.5-flash"),
        "structured_output_required": True,
        "evidence_required": True,
        "confidence_required": True,
        "policy_validation_required": True,
        "bounded_executor_required": True,
        "human_gate_preserved": True,
        "network_execution_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "production_change_authorized": False,
        "main_branch_change_authorized": False,
        "external_action_authorized": False,
        "flow": (
            "collect_orchestrator_state",
            "build_bounded_context",
            "request_structured_reasoning",
            "validate_schema",
            "validate_policy",
            "apply_human_gate_if_required",
            "hand_off_to_bounded_executor",
            "observe_result",
        ),
    }


def validate_gemini_orchestrator_driver_design():
    design = build_gemini_orchestrator_driver_design()
    assert design["role"] == "reasoning_driver"
    assert design["structured_output_required"] is True
    assert design["policy_validation_required"] is True
    assert design["bounded_executor_required"] is True
    assert design["human_gate_preserved"] is True
    assert design["network_execution_authorized"] is False
    assert design["secret_access_authorized"] is False
    assert design["commerce_authorized"] is False
    assert design["production_change_authorized"] is False
    assert design["main_branch_change_authorized"] is False
    assert design["external_action_authorized"] is False
    return True
