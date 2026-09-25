"""Tests for Gemini live call runtime design."""

from research_lab.sandbox_gemini_live_call_runtime_design import (
    build_runtime_policy,
    build_runtime_request,
    classify_runtime_result,
    validate_runtime_policy,
)


def run_tests():
    assert validate_runtime_policy() is True

    request = build_runtime_request(
        "gemini-3.8-flash",
        "Return structured candidate ranking.",
        "warashibe_orchestrator_decision_v1",
        "gate-001",
    )
    assert request["valid"] is True
    assert request["model"] == "gemini-3.8-flash"
    assert request["network_execution_authorized"] is False
    assert request["secret_read_authorized"] is False
    assert request["gemini_api_call_authorized"] is False

    invalid = build_runtime_request(
        "gemini-unknown",
        "",
        "",
        "",
    )
    assert invalid["valid"] is False
    assert "unsupported_model" in invalid["errors"]
    assert "invalid_prompt" in invalid["errors"]
    assert "invalid_schema_name" in invalid["errors"]
    assert "invalid_gate_token_id" in invalid["errors"]

    assert classify_runtime_result(200) == "parse_and_validate"
    assert classify_runtime_result(429) == "retry_same_model_then_fallback"
    assert classify_runtime_result(503) == "retry_same_model_then_fallback"
    assert classify_runtime_result(403) == "stop"
    assert classify_runtime_result(404) == "stop"
    assert classify_runtime_result(None) == "network_failure"

    policy = build_runtime_policy()
    assert policy["one_shot_gate_token_required"] is True
    assert policy["gate_token_reuse_forbidden"] is True
    assert policy["fallback_only_on_retryable_failure"] is True
    assert policy["stop_on_auth_config_error"] is True
    assert policy["gemini_api_call_authorized"] is False
    assert policy["external_action_authorized"] is False


if __name__ == "__main__":
    run_tests()
    print("sandbox Gemini live call runtime design tests passed")
