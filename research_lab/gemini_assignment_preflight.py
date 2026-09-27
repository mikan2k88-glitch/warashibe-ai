"""Fail-closed offline preflight for a *future* single Gemini research assignment.

This module never sends a request, reads secrets, or grants execution authority.
Budget figures are explicit per-attempt ceilings, not claims about provider pricing.
"""


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
    for field in ("max_requests", "max_input_tokens", "max_output_tokens", "max_cost_usd"):
        value = state.get(field)
        if type(value) not in (int, float) or value <= 0:
            errors.append("invalid_" + field)
    if state.get("max_requests") != 1:
        errors.append("request_limit_must_be_one")
    if state.get("max_input_tokens", 0) > 2000:
        errors.append("input_token_limit_exceeded")
    if state.get("max_output_tokens", 0) > 512:
        errors.append("output_token_limit_exceeded")
    if state.get("max_cost_usd", 0) > 0.10:
        errors.append("cost_limit_exceeded")
    if state.get("estimated_cost_usd") is None or type(state.get("estimated_cost_usd")) not in (int, float):
        errors.append("missing_cost_estimate")
    elif not (0 <= state["estimated_cost_usd"] <= state.get("max_cost_usd", -1)):
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
