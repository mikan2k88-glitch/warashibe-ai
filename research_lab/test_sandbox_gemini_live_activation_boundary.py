"""Tests for Gemini live activation boundary."""

from research_lab.sandbox_gemini_live_activation_boundary import (
    build_sandbox_gemini_live_activation_boundary,
    evaluate_activation_request,
    validate_sandbox_gemini_live_activation_boundary,
)


def _ready_state():
    return {
        "latest_ci_green": True,
        "sandbox_only": True,
        "bounded_context_ready": True,
        "structured_output_schema_ready": True,
        "gemini_api_key_present": True,
        "network_gate_approved": True,
        "secret_read_gate_approved": True,
        "human_gate_approved": True,
        "model": "gemini-3.8-flash",
        "requested_capabilities": ("rank_candidates",),
    }


def run_tests():
    assert validate_sandbox_gemini_live_activation_boundary() is True

    ready = evaluate_activation_request(_ready_state())
    assert ready["ready"] is True
    assert ready["selected_model"] == "gemini-3.8-flash"
    assert ready["network_execution_authorized"] is False
    assert ready["secret_read_authorized"] is False
    assert ready["gemini_api_call_authorized"] is False
    assert ready["requires_runtime_gate_consumption"] is True

    missing_gate = _ready_state()
    missing_gate["human_gate_approved"] = False
    rejected = evaluate_activation_request(missing_gate)
    assert rejected["ready"] is False
    assert "missing_human_gate_approved" in rejected["errors"]

    forbidden = _ready_state()
    forbidden["requested_capabilities"] = ("purchase_item",)
    blocked = evaluate_activation_request(forbidden)
    assert blocked["ready"] is False
    assert "forbidden_capability_requested" in blocked["errors"]
    assert blocked["forbidden_capabilities"] == ("purchase_item",)

    unsupported = _ready_state()
    unsupported["model"] = "gemini-unknown"
    bad_model = evaluate_activation_request(unsupported)
    assert bad_model["ready"] is False
    assert "unsupported_model" in bad_model["errors"]

    boundary = build_sandbox_gemini_live_activation_boundary()
    assert boundary["human_gate_required"] is True
    assert boundary["network_execution_authorized"] is False
    assert boundary["commerce_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Gemini live activation boundary tests passed")
