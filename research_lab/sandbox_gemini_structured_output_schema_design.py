"""Structured output schema for Gemini Orchestrator decisions.

This module validates model output after JSON parsing. It does not call Gemini,
read secrets, or authorize execution.
"""

SANDBOX_GEMINI_STRUCTURED_OUTPUT_SCHEMA_VERSION = "0.1"

ALLOWED_DECISION_TYPES = (
    "select_next_theme",
    "rank_candidates",
    "summarize_market_evidence",
    "propose_risk_action",
    "propose_kaizen_experiment",
    "prepare_executor_request",
    "analyze_ci_failure",
)

ALLOWED_ACTIONS = (
    "continue_research",
    "hold",
    "request_more_evidence",
    "prepare_executor_request",
    "prepare_human_gate",
    "reject_candidate",
)

REQUIRED_FIELDS = (
    "schema_version",
    "decision_type",
    "summary",
    "recommended_action",
    "confidence",
    "evidence_refs",
    "requires_human_gate",
    "risk_flags",
)


def validate_structured_output(payload):
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "errors": ("payload_not_mapping",),
            "execution_authorized": False,
        }

    errors = []
    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing_{field}")

    if payload.get("schema_version") != SANDBOX_GEMINI_STRUCTURED_OUTPUT_SCHEMA_VERSION:
        errors.append("unsupported_schema_version")

    if payload.get("decision_type") not in ALLOWED_DECISION_TYPES:
        errors.append("unsupported_decision_type")

    if payload.get("recommended_action") not in ALLOWED_ACTIONS:
        errors.append("unsupported_recommended_action")

    summary = payload.get("summary")
    if not isinstance(summary, str) or not summary.strip():
        errors.append("invalid_summary")

    confidence = payload.get("confidence")
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        errors.append("invalid_confidence")
    elif not 0 <= confidence <= 1:
        errors.append("confidence_out_of_range")

    evidence_refs = payload.get("evidence_refs")
    if not isinstance(evidence_refs, list):
        errors.append("invalid_evidence_refs")
    elif not all(isinstance(item, str) and item.strip() for item in evidence_refs):
        errors.append("invalid_evidence_ref_item")

    if not isinstance(payload.get("requires_human_gate"), bool):
        errors.append("invalid_requires_human_gate")

    risk_flags = payload.get("risk_flags")
    if not isinstance(risk_flags, list):
        errors.append("invalid_risk_flags")
    elif not all(isinstance(item, str) and item.strip() for item in risk_flags):
        errors.append("invalid_risk_flag_item")

    return {
        "valid": not errors,
        "errors": tuple(errors),
        "execution_authorized": False,
        "commerce_authorized": False,
        "requires_policy_validation": True,
    }


def build_schema_contract():
    return {
        "version": SANDBOX_GEMINI_STRUCTURED_OUTPUT_SCHEMA_VERSION,
        "mode": "post_parse_validation",
        "required_fields": REQUIRED_FIELDS,
        "allowed_decision_types": ALLOWED_DECISION_TYPES,
        "allowed_actions": ALLOWED_ACTIONS,
        "additional_fields_allowed": False,
        "confidence_range": (0.0, 1.0),
        "evidence_refs_required": True,
        "risk_flags_required": True,
        "human_gate_flag_required": True,
        "policy_validation_required": True,
        "bounded_executor_required": True,
        "network_execution_authorized": False,
        "gemini_api_call_authorized": False,
        "secret_access_authorized": False,
        "commerce_authorized": False,
        "external_action_authorized": False,
    }
