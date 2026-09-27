"""Fail-closed offline preflight for a *future* single Gemini research assignment.

This module never sends a request, reads secrets, or grants execution authority.
Budget figures are explicit per-attempt ceilings, not claims about provider pricing.
"""
import math


def _positive_finite_number(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def review_assignment_preflight(state):
    errors = []
    if not isinstance(state, dict):
        state = {}
        errors.append("invalid_state")
    for field in (
        "sandbox_only", "latest_ci_green", "ci_sha_matches_head",
        "authenticated_entry", "durable_shared_ledger_verified",
        "network_gate_approved", "secret_read_gate_approved",
        "human_gate_approved", "structured_output_ready",
    ):
        if state.get(field) is not True:
            errors.append("missing_" + field)
    for field in ("assignment_id", "source_run_id"):
        value = state.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > 256:
            errors.append("invalid_" + field)
    for field in ("max_requests", "max_input_tokens", "max_output_tokens"):
        value = state.get(field)
        if type(value) is not int or value <= 0:
            errors.append("invalid_" + field)
    cost_limit = state.get("max_cost_usd")
    if not _positive_finite_number(cost_limit):
        errors.append("invalid_max_cost_usd")
    if type(state.get("max_requests")) is not int or state["max_requests"] != 1:
        errors.append("request_limit_must_be_one")
    input_limit = state.get("max_input_tokens")
    if type(input_limit) is int and input_limit > 2000:
        errors.append("input_token_limit_exceeded")
    output_limit = state.get("max_output_tokens")
    if type(output_limit) is int and output_limit > 512:
        errors.append("output_token_limit_exceeded")
    if _positive_finite_number(cost_limit) and cost_limit > 0.10:
        errors.append("cost_limit_exceeded")
    estimate = state.get("estimated_cost_usd")
    if type(estimate) not in (int, float) or not math.isfinite(estimate) or estimate < 0:
        errors.append("missing_cost_estimate")
    elif _positive_finite_number(cost_limit) and estimate > cost_limit:
        errors.append("estimated_cost_exceeds_limit")
    if state.get("requested_capabilities") not in ([], ()):
        errors.append("capabilities_must_be_empty")
    return {
        "ready_for_separate_runtime_review": not errors,
        "errors": tuple(dict.fromkeys(errors)),
        "gemini_api_call_authorized": False,
        "network_execution_authorized": False,
        "secret_read_authorized": False,
        "codex_execution_authorized": False,
        "main_write_authorized": False,
        "commerce_authorized": False,
    }
