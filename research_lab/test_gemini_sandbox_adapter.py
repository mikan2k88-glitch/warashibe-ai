"""Tests for the offline Gemini sandbox adapter."""

from research_lab.gemini_sandbox_adapter import (
    build_model_attempt_plan,
    build_offline_adapter_snapshot,
    classify_http_error,
    evaluate_probe_payload,
    extract_response_text,
)


def run_tests():
    payload = {
        "candidates": [{
            "content": {
                "parts": [
                    {"thought": True, "text": "hidden reasoning"},
                    {"text": "WARASHIBE_GEMINI_OK"},
                ]
            }
        }]
    }
    assert extract_response_text(payload) == "WARASHIBE_GEMINI_OK"
    assert evaluate_probe_payload(payload)["ok"] is True

    multi = {
        "candidates": [{
            "content": {"parts": [{"text": "A"}, {"text": "B"}]}
        }]
    }
    assert extract_response_text(multi) == "A\nB"

    assert classify_http_error(429) == "retry_then_fallback"
    assert classify_http_error(503) == "retry_then_fallback"
    assert classify_http_error(403) == "stop"
    assert classify_http_error(404) == "stop"
    assert classify_http_error(None) == "network_failure"

    plan = build_model_attempt_plan()
    assert plan == (
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
    )
    assert len(plan) == len(set(plan))

    snapshot = build_offline_adapter_snapshot()
    assert snapshot["mode"] == "offline_sandbox"
    assert snapshot["network_execution_authorized"] is False
    assert snapshot["secret_access_authorized"] is False
    assert snapshot["external_action_authorized"] is False
    assert snapshot["requires_live_human_gate"] is True

    assert extract_response_text(None) == ""
    assert evaluate_probe_payload({})["ok"] is False


if __name__ == "__main__":
    run_tests()
    print("gemini sandbox adapter tests passed")
